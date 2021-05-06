"""
Package containg the binding for the core of Sofa
-------------------------------------------------

Example of use:
  .. code-block:: python

    import Sofa.Core
    import Sofa.Simulation
    import SofaRuntime
    SofaRuntime.importPlugin("SofaAllCommonComponents")

    n = Sofa.Core.Node("MyNode")
    n.addChild("Node2")
    n.addObject("MechanicalObject", name="dofs")

    Sofa.Simulation.init(n)
    Sofa.Simulation.print(n)

Submodules:
  .. autosummary::
    :toctree: _autosummary

    Sofa.Core
    Sofa.Simulation
    Sofa.Types
    Sofa.Helper
"""

import sys
import os
import inspect
import functools
import traceback
import Sofa.Helper
import Sofa.Core
import importlib

__all__=["animation"]

# Keep a list of the modules always imported in the Sofa-PythonEnvironment
try:
    __SofaPythonEnvironment_importedModules__
except:
    __SofaPythonEnvironment_importedModules__ = sys.modules.copy()

    # some modules could be added here manually and can be modified procedurally
    # e.g. plugin's modules defined from c++
    __SofaPythonEnvironment_modulesExcludedFromReload = []


def unloadModules():
    """ call this function to unload python modules and to force their reload
        (useful to take into account their eventual modifications since
        their last import).
    """
    global __SofaPythonEnvironment_importedModules__
    toremove = [name for name in sys.modules if not name in __SofaPythonEnvironment_importedModules__ and not name in __SofaPythonEnvironment_modulesExcludedFromReload ]
    for name in toremove:
        del(sys.modules[name]) # unload it


def formatStackForSofa(o):
    """ format the stack trace provided as a parameter into a string like that:
        in filename.py:10:functioname()
          -> the line of code.
        in filename2.py:101:functioname1()
            -> the line of code.
        in filename3.py:103:functioname2()
              -> the line of code.
    """
    ss='Python Stack: \n'
    for entry in o:
        ss+= ' in ' + str(entry[1]) + ':' + str(entry[2]) + ':'+ entry[3] + '()  \n'
        ss+= '  -> '+ entry[4][0] + '  \n'
        return ss


def getStackForSofa():
    """returns the current stack with a "informal" formatting. """
    ## we exclude the first level in the stack because it is the getStackForSofa() function itself.
    ss=inspect.stack()[1:]
    return formatStackForSofa(ss)


def getPythonCallingPointAsString():
    """returns the last entry with an "informal" formatting. """

    ## we exclude the first level in the stack because it is the getStackForSofa() function itself.
    ss=inspect.stack()[-1:]
    return formatStackForSofa(ss)


def getPythonCallingPoint():
    """returns the tupe with closest filename & line. """
    ## we exclude the first level in the stack because it is the getStackForSofa() function itself.
    ss=inspect.stack()[1]
    tmp=(os.path.abspath(ss[1]), ss[2])
    return tmp


def sendMessageFromException(e):
    exc_type, exc_value, exc_tb = sys.exc_info()
    sofaExceptHandler(exc_type, exc_value, exc_tb)


def sofaFormatHandler(type, value, tb):
    global oldexcepthook
    """This exception handler, convert python exceptions & traceback into more classical sofa error messages of the form:
       Message Description
       Python Stack (most recent are at the end)
          File file1.py line 4  ...
          File file1.py line 10 ...
          File file1.py line 40 ...
          File file1.py line 23 ...
            faulty line
    """
    s="\nPython Stack (most recent are at the end): \n"
    for line in traceback.format_tb(tb):
        s += line

    return repr(value)+"\n"+s


def getSofaFormattedStringFromException(e):
    exc_type, exc_value, exc_tb = sys.exc_info()
    return sofaFormatHandler(exc_type, exc_value, exc_tb)

def sofaExceptHandler(type, value, tb):
    global oldexcepthook
    """This exception handler, convert python exceptions & traceback into more classical sofa error messages of the form:
       Message Description
       Python Stack (most recent are at the end)
          File file1.py line 4  ...
          File file1.py line 10 ...
          File file1.py line 40 ...
          File file1.py line 23 ...
            faulty line
    """
    h = type.__name__

    if str(value) != '':
        h += ': ' + str(value)
    
    s = ''.join(traceback.format_tb(tb))
    
    Sofa.Helper.msg_error(h + '\n' + s, "line", 7)

sys.excepthook=sofaExceptHandler

def pyType2sofaType(v):
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, str):
        return "string"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "double"
    if isinstance(v, list) and len(v)==3:
        return "Vec3d"
    return None


class Prefab(Sofa.Core.RawPrefab):
    def __init__(self, *args, **kwargs):
        Sofa.Core.RawPrefab.__init__(self, *args, **kwargs)
        frame = inspect.currentframe().f_back
        frameinfo = inspect.getframeinfo(frame)
        definedloc = (frameinfo.filename, frameinfo.lineno)

        self.setDefinitionSourceFileName(definedloc[0])
        self.setDefinitionSourceFilePos(definedloc[1])
        self.setSourceTracking(definedloc[0])

        frame = frame.f_back
        if frame is not None:
            frameinfo = inspect.getframeinfo(frame)
            definedloc = (frameinfo.filename, frameinfo.lineno)
            self.setInstanciationSourceFileName(definedloc[0])
            self.setInstanciationSourceFilePos(definedloc[1])

        self.setName(str(self.__class__.__name__))
        self.addData("prefabname", value=type(self).__name__, type="string", group="Infos", help="Name of the prefab")
        self.addData("docstring", value=self.__doc__, type="string", group="Infos", help="Name of the prefab")
        self.init()

def msg_error(target, message):
    frameinfo = inspect.getframeinfo(inspect.currentframe().f_back)
    Sofa.Helper.msg_error(target, message, frameinfo.filename, frameinfo.lineno)

def msg_info(target, message):
    frameinfo = inspect.getframeinfo(inspect.currentframe().f_back)
    Sofa.Helper.msg_info(target, message, frameinfo.filename, frameinfo.lineno)

def msg_warning(target, message):
    frameinfo = inspect.getframeinfo(inspect.currentframe().f_back)
    Sofa.Helper.msg_warning(target, message, frameinfo.filename, frameinfo.lineno)

def msg_deprecated(target, message):
    frameinfo = inspect.getframeinfo(inspect.currentframe().f_back)
    Sofa.Helper.msg_deprecated(target, message, frameinfo.filename, frameinfo.lineno)

import inspect
def PrefabBuilder(f):
        frameinfo = inspect.getframeinfo(inspect.currentframe().f_back)
        definedloc = (frameinfo.filename, frameinfo.lineno)

        def SofaPrefabF(*args, **kwargs):
            class NodeHook(object):
                    def __init__(self, node):
                        self.node = node

                    def addChild(self, name):
                        return selfnode

                    def __getattr__(self, name):
                        return getattr(self.node, name)

            class InnerSofaPrefab(Sofa.Core.RawPrefab):
                def __init__(self, *args, **kwargs):
                    Sofa.Core.RawPrefab.__init__(self, *args, **kwargs)
                    self.isValid = True

                def doReInit(self):
                    if not self.isValid:
                        return
                    try:
                        argnames = inspect.getfullargspec(f).args

                        kkwargs = {}
                        kkwargs[argnames[0]] = self
                        for name in argnames[1:]:
                            kkwargs[name] = self.__data__[name].value

                        self.cb(**kkwargs)
                    except Exception as e:
                        self.isValid = False
                        exc_type, exc_value, exc_tb = sys.exc_info()
                        Sofa.Helper.msg_error(self, "Unable to build prefab  \n  "+getSofaFormattedStringFromException(e))
            try:
                selfnode = None
                kwargs["name"] = kwargs.get("name", f.__code__.co_name)
                selfnode = InnerSofaPrefab(*args, **kwargs)
                selfnode.setDefinitionSourceFileName(definedloc[0])
                selfnode.setDefinitionSourceFilePos(definedloc[1])
                selfnode.setSourceTracking(definedloc[0])
                selfnode.cb = f
                ## retrieve meta data from decorated class:
                selfnode.addData(name="prefabname", value=f.__code__.co_name,
                         type="string", help="The prefab's name", group="Infos")
                selfnode.addData(name="docstring", value=f.__doc__,
                         type="string", help="This prefab's docstring", group="Infos")

                ## Now we retrieve all params passed to the prefab and add them as datafields:
                argnames = inspect.getfullargspec(f).args
                defaults = inspect.getfullargspec(f).defaults
                print("ICA ")

                if argnames is None:
                    argnames = []
                    defaults = []

                if defaults is None:
                    defaults = []

                i = len(argnames) - len(defaults)
                for n in range(0, len(defaults)):
                    if argnames[i+n] not in selfnode.__data__:
                        selfnode.addPrefabParameter(name=argnames[i+n],
                                                    value=kwargs.get(argnames[i+n], defaults[n]),
                                                    type=pyType2sofaType(defaults[n]), help="Undefined")

                selfnode.init()

            except Exception as e:
                if selfnode is not None:
                    selfnode.isValid=False
                    Sofa.Helper.msg_error(selfnode, "Unable to create prefab because: "+getSofaFormattedStringFromException(e))
                else:
                    Sofa.Helper.msg_error("PrefabBuilder", "Unable to create prefab because: "+getSofaFormattedStringFromException(e))
            return selfnode
        SofaPrefabF.__dict__["__original__"] = f
        return SofaPrefabF

