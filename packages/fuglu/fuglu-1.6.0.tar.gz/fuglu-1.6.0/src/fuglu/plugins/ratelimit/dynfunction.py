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
#
import typing as tp
import re
import logging


FUNCTION_KEYWORD = "<func>"
BE_VERBOSE = False


class NoFunctionDef(Exception):
    pass


class FunctionDefError(Exception):
    pass


def toint(intstring: str) -> int:
    return int(intstring)


def isint(input):
    return "Is Integer" if isinstance(input, int) else "NOT AN Integer"


def bla(*args, **kwargs):
    print(f"Hello from bla...\n"
          f"args: {args}\n"
          f"kwargs: {kwargs}")


FUNCMAP = {f.__name__:f for f in [toint, isint, bla]}


findargs = re.compile(r"^[^\(]+\((?P<arguments>\S*)\)")
findreturn = re.compile(r"\[([0-9]+)\]")
findinteger = re.compile(r"^\(int\)(?P<integer>[0-9]+)$")
findfloat = re.compile(r"^\(float\)(?P<float>[0-9\.]+)$")
findbool = re.compile(r"^\(bool\)(?P<boolean>[TtrueFfals]+)$")
findfunctionname = re.compile(r"^[\w.]+")


def isiterable(object: tp.Any) -> bool:
    try:
        _ = iter(object)
    except TypeError:
        return False
    # we don't want to iterate over strings
    return not isinstance(object, (str, bytes, bytearray))


class FunctionWrapperInt:
    def __init__(self, definitionstring: str, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


class FunctionWrapper(FunctionWrapperInt):
    def __init__(self, definitionstring: str, **kwargs):
        """Load a function (and keyword args) from a string"""
        super().__init__(definitionstring=definitionstring, **kwargs)
        functionstring = definitionstring.strip()

        # get function from name
        try:
            functionname = findfunctionname.search(functionstring)
            functionname = functionname.group(0)
        except Exception:
            raise FunctionDefError(f"{functionstring} doesnt contain a function name")

        self.logger = logging.getLogger(f'fuglu.FunctionWrapper({functionname})')
        if BE_VERBOSE:
            self.logger.debug(f"full def: {definitionstring}")
            self.logger.debug(f"functionstring: {functionstring}")
            self.logger.debug(f"functionname: {functionname}")

        # parse argument dict
        args = findargs.search(functionstring)
        kwargs = {}
        passkwargs = []
        if args:
            args = args.group('arguments')
            args = args.strip(' ()')
            args = args.split(',')
            for arg in args:
                try:
                    k, v = arg.split("=")
                    if v:
                        matchint = findinteger.search(v)
                        matchfloat = findfloat.search(v)
                        matchbool = findbool.search(v)
                        if matchint:
                            v = int(matchint['integer'])
                        elif matchfloat:
                            v = float(matchfloat['float'])
                        elif matchbool:
                            booleanstring = matchbool['boolean']
                            v = booleanstring.lower() not in ['false', '1']
                        kwargs[k] = v
                    else:
                        passkwargs.append(k)
                except ValueError:
                    pass

        if BE_VERBOSE:
            self.logger.debug(f"kwargs = {kwargs}")
        self.kwargs = kwargs

        if BE_VERBOSE:
            self.logger.debug(f"pass kwargs = {passkwargs}")
        self.passkwargs = passkwargs

        # parse return value values selection
        returnargs = findreturn.findall(functionstring)
        returnargs = [int(r.strip()) for r in returnargs if r.strip()]
        if BE_VERBOSE:
            self.logger.debug(f"returnargs = {returnargs}")
        self.returnargs = returnargs

        # get function
        funcname = functionname.rsplit(".", 1)
        funcname = [f for f in funcname if f.strip()]

        func = None
        if len(funcname) > 1:
            modname, funcname = funcname
            try:
                module = __import__(modname, fromlist=[funcname])
                func = getattr(module, funcname)
            except Exception:
                func = None
        else:
            funcname = funcname[0]
            try:
                func = FUNCMAP[funcname]
            except KeyError:
                func = None
        if func is None:
            raise Exception(f"Couldn't find function {functionname}")

        self.func = func

    def _process_return(self, result):

        if self.returnargs and result is not None:
            if isiterable(result):
                if len(self.returnargs) > 1 and len(result) > 0:
                    result = [result[i] for i in self.returnargs]
                else:
                    result = result[self.returnargs[0]]
        return result

    def __call__(self, *args, **kwargs):
        if self.kwargs:
            indict = self.kwargs
        elif kwargs:
            indict = kwargs
        else:
            indict = None

        # kwargs to pass
        if self.passkwargs and indict:
            selected = {}
            for passarg in self.passkwargs:
                if passarg in indict:
                    selected[passarg] = indict[passarg]
                elif passarg in kwargs:
                    selected[passarg] = kwargs[passarg]
            indict = selected

        # make sure the internally stored items are present...
        for k, v in self.kwargs.items():
            if k not in indict:
                indict[k] = v

        result = self.func(*args, **indict) if indict else self.func(*args)
        return self._process_return(result)


class MultipleFunctionsWrapper(object):
    PROCDICT = {
        FUNCTION_KEYWORD: FunctionWrapper
    }

    def __init__(self, funclist: tp.List[str],
                 processordict: tp.Optional[tp.Dict[str, FunctionWrapperInt]] = None,
                 DefaultProcessorClass: tp.Optional[FunctionWrapperInt] = None, **kwargs):
        if not funclist:
            raise FunctionDefError("Function list is empty!")

        self.logger = logging.getLogger('fuglu.MultipleFunctionsWrapper')
        self.functions = []

        classdict = processordict if processordict is not None else MultipleFunctionsWrapper.PROCDICT

        for definitionstring in funclist:
            if BE_VERBOSE:
                self.logger.debug(f"Process \"{definitionstring}\"")
            definitionstring = definitionstring.strip()

            newfunc = None
            for key, ProcClass in classdict.items():
                if definitionstring.startswith(key):
                    functionstring = definitionstring[len(key):].strip()
                    newfunc = FunctionWrapper(definitionstring=functionstring, **kwargs)
                    break

            if not newfunc and DefaultProcessorClass:
                newfunc = DefaultProcessorClass(definitionstring=definitionstring, **kwargs)

            if not newfunc:
                raise FunctionDefError(f"{definitionstring} doesnt contain a function name")

            self.functions.append(newfunc)

    def __call__(self, *args, **kwargs):
        previousresult = args
        for func in self.functions:
            if isiterable(previousresult):
                previousresult = func(*previousresult, **kwargs)
            else:
                previousresult = func(previousresult, **kwargs)
        return previousresult
