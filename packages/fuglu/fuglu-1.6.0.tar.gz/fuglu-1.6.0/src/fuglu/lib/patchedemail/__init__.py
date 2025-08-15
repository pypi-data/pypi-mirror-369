import sys
if sys.version_info >= (3, 10, 0):
    # should be fixed in python 3.10, see https://bugs.python.org/issue27321
    from email.message import EmailMessage as PatchedMessage
    from email.mime.multipart import MIMEMultipart as PatchedMIMEMultipart
else:
    from .message import PatchedMessage
    from .message import PatchedMIMEMultipart
