# -*- coding: UTF-8 -*-
#   Copyright Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
import logging
import os
import email
import base64
import typing as tp
import re
from fuglu.shared import ScannerPlugin, DUNNO, AppenderPlugin, Suspect, FileList, actioncode_to_string, FuConfigParser
from fuglu.bounce import FugluSMTPClient, SMTPException, Bounce
from fuglu.lib.patchedemail import PatchedMessage, PatchedMIMEMultipart
from email.mime.base import MIMEBase
    

# https://m2crypto.readthedocs.io/en/latest/howto.smime.html
# https://stackoverflow.com/questions/57451015/decrypting-s-mime-with-python3-openssl-library
# https://stackoverflow.com/questions/15700945/how-to-get-the-signed-content-from-a-pkcs7-envelop-with-m2crypto
# https://stackoverflow.com/questions/34625271/getting-pkcs7-signer-chain-in-python
# https://gitlab.com/rhab/python-smail/-/blob/master/smail/sign.py
# https://code.activestate.com/recipes/285211-verifying-smime-signed-email-with-m2crypto-and-no-/
# https://pypi.org/project/endesive/
# https://datatracker.ietf.org/doc/html/rfc1847
# https://datatracker.ietf.org/doc/html/rfc8551

# broken:
# openssl smime -decrypt -in /tmp/encdata.txt -recip venv/fuglu/certs/store/test@fuglu.org.crt -inkey venv/fuglu/certs/store/test@fuglu.org.key
# works:
# openssl cms -decrypt -in /tmp/encrypted.eml -recip venv/fuglu/certs/store/test@fuglu.org.crt -inkey venv/fuglu/certs/store/test@fuglu.org.key


try:
    from endesive import verifier, signer, email as email_smime
    from cryptography.hazmat.primitives.serialization import load_pem_private_key, pkcs7, Encoding
    from cryptography.x509 import load_pem_x509_certificate, Certificate
    HAVE_ENDESIVE = True
except ImportError:
    HAVE_ENDESIVE = False


def copy_headers(source, target, skip_headers=None):
    """
    copy headers from one email message object to another.
    some headers such as content-type, mime-version, or content-transfer-encoding are always skipped
    :param source: source email/mime message object
    :param target: target email/mime message object
    :param skip_headers: additional headers to be skipped
    :return: target email message object augmented by additional headers
    """
    hdrs_copied = {"content-type", "mime-version", "content-transfer-encoding"}
    if skip_headers:
        for item in hdrs_copied:
            hdrs_copied.add(item.lower())
    for hdr_name in source.keys():
        hdr_name = hdr_name.lower()
        if hdr_name in hdrs_copied:
            continue
        values = source.get_all(hdr_name, [])
        for value in values:
            target.add_header(hdr_name, value)
        hdrs_copied.add(hdr_name)
    return target


class MultiPEMList(FileList):
    """
    reads a file containing multiple pem formatted certificates.
    returns a list of individual pem certificate strings.
    """
    # from https://github.com/hynek/pem/blob/main/src/pem/_core.py
    _re_pem = re.compile('----[- ](?P<be>BEGIN|END) (?P<ctype>CERTIFICATE|TRUSTED CERTIFICATE|NEW CERTIFICATE REQUEST|CERTIFICATE REQUEST|X509 CRL|PRIVATE KEY|ENCRYPTED PRIVATE KEY|PUBLIC KEY|RSA PRIVATE KEY|RSA PUBLIC KEY|EC PRIVATE KEY|DSA PRIVATE KEY|DH PARAMETERS|OPENSSH PRIVATE KEY|SSH2 PUBLIC KEY|SSH2 ENCRYPTED PRIVATE KEY|PGP PUBLIC KEY BLOCK|PGP PRIVATE KEY BLOCK)[- ]----')
    def _parse_lines(self, lines:tp.List[str]) -> tp.List[bytes]:
        certs = []
        cert = []
        in_cert = None
        for line in lines:
            line = line.strip()
            m = self._re_pem.match(line)
            if m:
                mg = m.groupdict()
                if mg.get('be') == 'BEGIN':
                    in_cert = mg.get('ctype')
                elif mg.get('be') == 'END':
                    if mg.get('ctype') != in_cert:
                        logger = logging.getLogger(f'fuglu.plugin.sigenc.{self.__class__.__name__}')
                        logger.error(f'error parsing file {self.filename}: expected cert block ending in {in_cert}, got {mg.get("ctype")}')
                    in_cert = None
                    cert.append(line)
                    certs.append('\n'.join(cert).encode())
                    cert = []
            if in_cert is not None:
                cert.append(line)
        return certs


class VerifyAnswer(object):
    def __init__(self):
        self.signed = False
        self.signature_ok = None
        self.certificate_ok = None
        self.signer_certs = {}
        self.error = None
    
    def __str__(self):
        return f'signed={self.signed} sigok={self.signature_ok} certok={self.certificate_ok}'


class DecryptVerify(ScannerPlugin):
    """
    This plugin decrypts encrypted mail and verifies signatures of signed mails.
    Currently only S/MIME is supported.
    Certificates found in signatures are extracted and stored in tag smime.learn_cert
    Verification result is added as spamassassin temp header
    
    WARNING: THIS PLUGIN ALTERS MAIL CONTENT!
    """
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self._ca_store = None
        self.requiredvars = {
            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER, REJECT)",
            },
            'ca_store': {
                'default': '/etc/ssl/certs/ca-certificates.crt',
                'description': "path to system's CA store file",
            },
        }
        
        
    def _init_ca_store(self):
        if self._ca_store is None:
            ca_store_path = self.config.get(self.section, 'ca_store')
            if ca_store_path and os.path.isfile(ca_store_path):
                self._ca_store = MultiPEMList(ca_store_path)
        
    
    def _get_smime_certs_from_sig(self, sig:bytes) -> tp.Dict[str,bytes]:
        certs = {}
        sigdata = pkcs7.load_der_pkcs7_certificates(sig)
        for cert in sigdata:
            cbytes = cert.public_bytes(Encoding.PEM)
            for attr in cert.subject:
                if attr.oid._name in ['emailAddress', 'Email']:
                    emailaddr = attr.value
                    certs[emailaddr] = cbytes
                    break
        return certs
    
    
    def verify_smime_sig(self, suspect:Suspect) -> VerifyAnswer:
        # see https://github.com/m32/endesive/blob/master/endesive/email/verify.py
        self._init_ca_store()
        answer = VerifyAnswer()
        
        msg = suspect.get_message_rep()
        sig = None
        plain = b''
        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                if ct in ['application/pkcs7-signature', 'application/x-pkcs7-signature']:
                    sig = part.get_payload(decode=True)
                    answer.signed = True
                elif ct == 'text/plain' and not part.is_attachment() and part.get_filename() is None:
                    plain = part.get_payload(decode=False).encode()
                
        if sig:
            trusted_cert_pems = self._ca_store.get_list()
            
            try:
                hashok, signatureok, certok = verifier.verify(sig, plain, trusted_cert_pems)
            except Exception as e:
                self.logger.warning(f'{suspect.id} failed to verify S/MIME signature due to {e.__class__.__name__}: {str(e)}')
                signatureok = False
                certok = False
            answer.signature_ok = signatureok
            answer.certificate_ok = certok
            
            if signatureok:
                certs = self._get_smime_certs_from_sig(sig)
                answer.signer_certs = certs
        
        return answer
    
    
    def decrypt_smime_data(self, suspect: Suspect) -> bool|None:
        privkey = suspect.get_tag('smime.privkeys', {}).get(suspect.to_address.lower())
        if privkey:
            key = load_pem_private_key(privkey, None)
        else:
            self.logger.warning(f'{suspect.id} no private key found for {suspect.to_address.lower()}')
            return None
        
        msgrep = suspect.get_message_rep()
        if msgrep.is_multipart():
            self.logger.debug(f'{suspect.id} multipart should not be S/MIME encrypted')
            return None
        
        if msgrep.get_content_type() not in ['application/pkcs7-mime', 'application/x-pkcs7-mime']:
            self.logger.debug(f'{suspect.id} not an S/MIME encrypted message (wrong content-type)')
            return None
        
        try:
            source = msgrep.as_string()
            newsource = email_smime.decrypt(source, key) # requires str, returns bytes
            if newsource == source:
                self.logger.debug(f'{suspect.id} nothing to S/MIME decrypt')
                return None
            if newsource:
                msgrep_new = email.message_from_bytes(newsource, _class=PatchedMessage)
                msgrep_new = copy_headers(msgrep, msgrep_new)
                suspect.set_message_rep(msgrep_new)
                return True
            else:
                self.logger.debug(f'{suspect.id} not an S/MIME encrypted message (no content extracted)')
                return False
        except Exception as e:
            self.logger.warning(f'{suspect.id} failed to S/MIME decrypt message to {suspect.to_address} due to {e.__class__.__name__}: {str(e)}')
            return False
    

    def examine(self, suspect:Suspect):
        if not HAVE_ENDESIVE:
            return DUNNO
        
        firstanswer = self.verify_smime_sig(suspect)
        if firstanswer.certificate_ok and firstanswer.signer_certs:
            suspect.set_tag('smime.learn_certs', firstanswer.signer_certs)
        
        decrypted = self.decrypt_smime_data(suspect)
        if decrypted is False:
            return self._problemcode(), 'message could not be decrypted'
        
        if firstanswer.signed and decrypted:
            self.logger.info(f'{suspect.id} message was signed after encryption')
        
        answer = self.verify_smime_sig(suspect)
        
        if firstanswer.signed and decrypted and answer.signed:
            self.logger.info(f'{suspect.id} triple wrapped message')
            answer.signature_ok = answer.signature_ok and firstanswer.signature_ok
        
        suspect.set_tag('smime.signed', answer.signed)
        suspect.set_tag('smime.signature_ok', answer.signature_ok)
        suspect.set_tag('smime.certificate_ok', answer.certificate_ok)
        if answer.certificate_ok and answer.signer_certs:
            certs = suspect.get_tag('smime.learn_certs', {})
            certs.update(answer.signer_certs)
            suspect.set_tag('smime.learn_certs', certs)
        
        if answer.signed and not answer.signature_ok:
            suspect.write_sa_temp_header('X-SMIME-VERIFY', 'fail')
            return self._problemcode(), answer.error
        elif not answer.signed:
            suspect.write_sa_temp_header('X-SMIME-VERIFY', 'none')
        elif answer.signature_ok and answer.certificate_ok:
            suspect.write_sa_temp_header('X-SMIME-VERIFY', 'pass') # signed and verified
        elif answer.signature_ok and not answer.certificate_ok:
            suspect.write_sa_temp_header('X-SMIME-VERIFY', 'sign') # self signed cert
        
        return DUNNO
    
    
    def lint(self):
        ok = self.check_config()
        if not HAVE_ENDESIVE:
            print('ERROR: endesive not found')
            ok = False
            
        ca_store = self.config.get(self.section, 'ca_store')
        if not ca_store:
            print('ERROR: ca_store not defined')
        elif not os.path.isfile(ca_store):
            print(f'ERROR: ca_store {ca_store} is not a file')
            ok = False
        return ok


class SignEncrypt(ScannerPlugin):
    """
    This plugin signs and encrypts mail.
    Currently only S/MIME is supported.
    Signature is based on sender keys found in smime.privkeys. Mail with calendar attachment is never signed as some mail clients are no longer able to process them.
    Encryption is based on recipient certificates found in tags smime.pubkeys.
    see plugin LoadSMIMECert for how to load certificates.
    
    WARNING: THIS PLUGIN ALTERS MAIL CONTENT!
    """
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self._ca_store = None
        self.requiredvars = {
            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER, REJECT)",
            },
            'hash_algo': {
                'default': 'sha256',
                'description': "the hash algorithm used for signing",
            },
            'use_pss': {
                'default': 'False',
                'description': "use PSS for signing",
            },
            'enc_algo': {
                'default': 'aes256_ofb',
                'description': "the algorithm used for encryption",
            },
            'use_oaep': {
                'default': 'False',
                'description': "use OAEP for encryption",
            },
            'use_triple_wrap': {
                'default': 'False',
                'description': "sign again after encryption",
            },
            'new_subject': {
                'default': '',
                'description': "Subject to be set after encryption. Leave empty to use original subject.",
            }
        }
    
    def _mk_mime_sig(self, sigdata:bytes, sigtype:str, filename:str="smime.p7s") -> MIMEBase:
        sig = MIMEBase(_maintype='application', _subtype=sigtype, name=filename)
        sig.add_header('Content-Disposition', 'attachment', filename=filename)
        sig.add_header('Content-Transfer-Encoding', 'base64')
        sig.set_payload(base64.encodebytes(sigdata))
        del sig['MIME-Version']
        return sig
    
    def sign_smime(self, suspect:Suspect, fromaddr:str|None) -> bool:
        if fromaddr is None:
            self.logger.warning(f'{suspect.id} no from address found, not signing')
            return False
        
        privkey = suspect.get_tag('smime.privkeys', {}).get(fromaddr)
        if privkey:
            key = load_pem_private_key(privkey, None)
        else:
            self.logger.warning(f'{suspect.id} no private key for {fromaddr}, not signing')
            return False
        
        pubkey = suspect.get_tag('smime.pubkeys', {}).get(fromaddr)
        if pubkey:
            x509 = load_pem_x509_certificate(pubkey)
        else:
            self.logger.warning(f'{suspect.id} no public key for {fromaddr}, not signing')
            return False
            
        pss = self.config.getboolean(self.section, 'use_pss')
        hashalgo = self.config.get(self.section, 'hash_algo')
        hashalgo_map = {
            'sha256': 'sha-256',
            'sha384': 'sha-384',
            'sha512': 'sha-512',
        }
        micalg = hashalgo_map.get(hashalgo, hashalgo)
        
        sigtype = 'pkcs7-signature'
        if pss:
            sigtype = 'x-pkcs7-signature'
        
        msgrep = suspect.get_message_rep()
        
        msgrep_new = PatchedMIMEMultipart(_subtype='signed')
        msgrep_new.set_param('protocol', f'application/{sigtype}')
        msgrep_new.set_param('micalg', micalg)
        msgrep_new.preamble = 'This is an S/MIME signed message\n'
        msgrep_new = copy_headers(msgrep, msgrep_new)
                
        if not msgrep.is_multipart():
            plain = msgrep.get_payload(decode=False).encode()
            plain = plain.replace(b'\n', b'\r\n')
            sigdata = signer.sign(plain, key, x509, [], hashalgo, pss=pss)
            sig = self._mk_mime_sig(sigdata, sigtype)
            body = MIMEBase(_maintype='text', _subtype='plain')
            body.set_param('charset', msgrep.get_content_charset())
            body.set_payload(plain)
            msgrep_new.attach(body)
            msgrep_new.attach(sig)
        else:
            plain = b''
            for part in msgrep.walk():
                ct = part.get_content_type()
                if ct == 'text/calendar':
                    self.logger.info(f'{suspect.id} found calendar attachment, not signing')
                    return False
                elif ct == 'text/plain' and not part.is_attachment() and part.get_filename() is None:
                    plain = part.get_payload(decode=False).encode()
                    plain = plain.replace(b'\n', b'\r\n')
            sigdata = signer.sign(plain, key, x509, [], hashalgo, pss=pss)
            sig = self._mk_mime_sig(sigdata, sigtype)
            container = PatchedMIMEMultipart(_subtype='alternative')
            for part in msgrep.walk():
                ct = part.get_content_type()
                if ct == 'text/plain' and not part.is_attachment() and part.get_filename() is None:
                    continue
                else:
                    container.attach(part)
            msgrep_new.attach(container)
            msgrep_new.attach(sig)
            
        suspect.set_message_rep(msgrep_new)
        return True
    
    
    def encrypt_smime(self, suspect:Suspect) -> bool:
        certs = []
        for rcpt in suspect.recipients:
            pubkey = suspect.get_tag('smime.pubkeys', {}).get(rcpt)
            if pubkey:
                certs.append(load_pem_x509_certificate(pubkey))
            else:
                self.logger.warning(f'{suspect.id} no public key for {rcpt}, cannot encrypt for all recipients')
                # todo: this case need be handled better. either reject mail in such case or split and generate a second message (using Bounce)
        if not certs:
            return False
        
        encalgo = self.config.get(self.section, 'enc_algo')
        use_oaep = self.config.getboolean(self.section, 'use_oaep')
        msgrep = suspect.get_message_rep()
        encrypted = email_smime.encrypt(msgrep.as_bytes(), certs, encalgo, use_oaep) # requires bytes, returns str
        msgrep_new = email.message_from_string(encrypted)
        msgrep_new = copy_headers(msgrep, msgrep_new)
        
        new_subject = self.config.get(self.section, 'new_subject')
        if new_subject:
            msgrep_new.replace_header('Subject', new_subject)
        
        suspect.set_message_rep(msgrep_new)
        return True
    
    
    def _get_fromaddr(self, suspect:Suspect) -> str|None:
        fromaddr = None
        sender = suspect.parse_from_type_header('From')
        if sender and sender[0]:
            fromaddr = sender[0][1]
        return fromaddr


    def examine(self, suspect:Suspect):
        if not HAVE_ENDESIVE:
            return DUNNO
        
        fromaddr = self._get_fromaddr(suspect)
        signed = self.sign_smime(suspect, fromaddr)
        suspect.set_tag('smime.added_signature', signed)
        encrypted = self.encrypt_smime(suspect)
        suspect.set_tag('smime.added_encryption', encrypted)
        
        use_triple_wrap = self.config.getboolean(self.section, 'use_triple_wrap')
        if use_triple_wrap and signed:
            signed = self.sign_smime(suspect, fromaddr)
            if signed:
                self.logger.debug(f'{suspect.id} messsage is triple wrapped')
        
        return DUNNO
    
    
    def lint(self):
        ok = self.check_config()
        if not HAVE_ENDESIVE:
            print('ERROR: endesive not found')
            ok = False
        return ok


class LoadSMIMECert(ScannerPlugin):
    """
    This plugin loads SMIME x509 keys and certificates for sender and recipient from disk.
    key file name must be user@domain.key
    certificate file name must be user@domain.crt
    key data must be in -----BEGIN PRIVATE KEY----- / -----END PRIVATE KEY-----
    certificate data must be in -----BEGIN CERTIFICATE----- / -----END CERTIFICATE-----
    TRUSTED CERTIFICATE is not supported (restriction in python cryptography)
    
    Tags added:
    smime.pubkeys - dict of email address: certificate data
    smime.privkeys - dict of email address: private key data
    """
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'certificate_store': {
                'default': '',
                'description': 'path to directory where local user certificates are stored. file name format should be user@domain.crt resp user@domain.key',
            },
        }
    
    
    def examine(self, suspect:Suspect):
        certificate_store = self.config.get(self.section, 'certificate_store')
        if not certificate_store or not os.path.isdir(certificate_store):
            return DUNNO
        
        emailaddresses = {suspect.to_address.lower()}
        if suspect.from_address:
            emailaddresses.add(suspect.from_address.lower())
        
        sender = suspect.parse_from_type_header('From')
        if sender and sender[0]:
            fromaddr = sender[0][1]
            if fromaddr:
                emailaddresses.add(fromaddr)
        
        pubkeys = {}
        privkeys = {}
        for emailaddr in emailaddresses:
            _basepath = os.path.join(certificate_store, f'{emailaddr}')
            certpath = _basepath + '.crt'
            keypath = _basepath + '.key'
            if os.path.isfile(certpath) and os.path.isfile(keypath):
                with open(certpath, 'rb') as f:
                    pubkeys[emailaddr] = f.read()
                with open(keypath, 'rb') as f:
                    privkeys[emailaddr] = f.read()
        
        suspect.set_tag('smime.pubkeys', pubkeys)
        suspect.set_tag('smime.privkeys', privkeys)
        return DUNNO
    
    
    def lint(self):
        ok = self.check_config()
        if not ok:
            return False
        
        certificate_store = self.config.get(self.section, 'certificate_store')
        if not certificate_store:
            print('ERROR: certificate_store not defined')
            return False
        elif not os.path.isdir(certificate_store):
            print(f'ERROR: certificate_store {certificate_store} does not exist or is not a directory')
            return False
        return True
    
    
    
class LearnSMIMECert(AppenderPlugin):
    """
    This plugin writes SMIME Certs that were learned during verification to disk
    """
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'pubkey_store': {
                'default': '',
                'description': 'path to directory where learned pubkeys are stored. leave empty to disable saving.',
            },
        }
        
    
    def process(self, suspect, decision):
        if suspect.get_tag('smime.signed') and suspect.get_tag('smime.verified'):
            certs = suspect.get_tag('smime.learn_cert')
            if not certs:
                self.logger.debug(f'{suspect.id} signed&verified but no cert...')
                return
            
            pubkey_store = self.config.get('pubkey_store')
            if not pubkey_store or not os.path.isdir(pubkey_store):
                return
            
            sender = suspect.parse_from_type_header('From')
            if sender and sender[0]:
                fromaddr = sender[0][1]
                
                for certemail in certs:
                    cert = certs[certemail]
                    if certemail and fromaddr:
                        certemail = certemail.lower()
                        if certemail == fromaddr.lower():
                            certpath = os.path.join(pubkey_store, f'{certemail}.crt')
                            with open(certpath, 'wb') as f:
                                f.write(cert)
                            self.logger.info(f'{suspect.id} learned cert for {certemail} as {certpath}')
                        else:
                            self.logger.debug(f'{suspect.id} ignoring cert for {certemail} in message from {fromaddr}')
    
    def lint(self):
        ok = self.check_config()
        pubkey_store = self.config.get(self.section, 'pubkey_store')
        if pubkey_store and not os.path.isdir(pubkey_store):
            print(f'ERROR: pubkey_store {pubkey_store} is not a directory')
            ok = False
        return ok
    
    
    
    
    
    
    
    