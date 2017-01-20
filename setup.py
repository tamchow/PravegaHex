# Compile to an executable
# Does not build on Python 3.5 with latest cx_Freeze - KeyError 'TCL_LIBRARY'.
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["os", "random", "threading", "pygame"]}
setup(name="Pravega Hex", version="2.5", description="Hex Game for Pravega Biology",
      options={"build_exe": build_exe_options}, executables=[Executable("hex.py", base="Win32GUI")],
      requires=['pygame'])
