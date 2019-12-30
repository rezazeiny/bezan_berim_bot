import os
import sys
if sys.platform == "win32":
    PYTHON_DIRECTORY = "\\".join(os.path.realpath(__file__).split("\\")[:-1])
    __all__ = [f.split(".")[0] for f in os.listdir(PYTHON_DIRECTORY) if
               os.path.isfile(os.path.join(PYTHON_DIRECTORY, f)) and f[0:2] != "__"]
else:
    PYTHON_DIRECTORY = "/".join(os.path.realpath(__file__).split("/")[:-1])
    __all__ = [f.split(".")[0] for f in os.listdir(PYTHON_DIRECTORY) if
               os.path.isfile(os.path.join(PYTHON_DIRECTORY, f)) and f[0:2] != "__"]

# print(__all__)
commands = {}
for module in __all__:
    print(module)
    mod = __import__("main_class." + module, fromlist=["*"])
    commands[module] = getattr(mod, module[0].upper() + module[1:].lower())

# print(commands)
# setattr("a", "b", "s")
# mod = __import__("main_class.start", fromlist=["*"])
