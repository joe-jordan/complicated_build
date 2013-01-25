complicated_build
=================

a python extension build system (with Cython support) which allows automated compilation a mixture of C, C++, FORTRAN and Cython sources without F2PY interference.

inspired by the problem in [this stackoverflow question](http://stackoverflow.com/questions/12696520/cython-and-fortran-how-to-compile-together-without-f2py).

Note, this library also provides a significant improvement on the default python build system for native extensions with many source files: by default it *caches all temporary build objects*, and only recompiles the particular source files that have changed. When debugging extensions, e.g. making small changes to one or two source files in a long list, this can present a significant time saving in each build/run stage.

example usage in a setup.py:

```python
import cb
from distutils.core import setup

global_includes = ['/opt/local/include/']
global_macros = [("__SOME_MACRO__",), ("__MACRO_WITH_VALUE__", "5")]

extensions = [{'name' : 'mylib.impl',
    'sources' : ['mylib/impl.pyx', 'clibs/some_other_code.cpp']
}]

import sys, os.path
if 'build' in sys.argv or ('install' in sys.argv and not os.path.exists('build')):
    cb.build(extensions, global_macros = global_macros, global_includes = global_includes)

import datetime
setup(
    name="mylib",
    version=datetime.date.today().strftime("%d%b%Y"),
    author="A N Other",
    author_email="a.other@domain.lol",
    url="http://",
    packages=["mylib"]
)
```

some default values to watch for:

```python
compiler = {
  'cpp' : 'g++',
  'c' : 'gcc',
  'f90' : 'gfortran'
}
```

if you want to support, for example, `F77` files you can do:

```python
cb.compiler['f'] = 'gfortran'
```

or, if you want to use the NAG fortran compilers:

```python
cb.compiler['f90'] = 'nagfor'
```

or if you're strange (cough cough) and use `.cxx` or `.cc` instead of `.cpp` you can do:

```python
cb.compiler['cxx'] = 'g++'
```

however, you may need to modify the function `cb._linker_vars` to better reflect what runtimes you need to link against (especially if you are mixing fortran and C++ sources.)

additionally, if you don't have Cython installed on your system, the program shouldn't crash (unless you're trying to compile `.pyx` files, of course) -- it only gets around to `import`ing Cython when it needs to `cythonize` the sources.

Finally, a more involved example:

```python
import cb
from distutils.core import setup
import numpy as np

global_includes = [np.get_include()]
global_macros = [("__FORCE_CPP__",)]

extensions = [
  {'name' : 'pywat.watershed',
    'sources' : [
      'pywat/watershed.pyx',
      'clibs/watershed.cpp',
      'clibs/stripack.f90',
      'clibs/tensors/D3Vector.cpp'
  ]},
  {'name' : 'pywat.shapes',
    'sources' : [
      'pywat/shapes.pyx',
      'clibs/custom_types/d3shape.cpp',
      'clibs/custom_types/sphere.cpp',
      'clibs/custom_types/polyhedron.cpp',
      'clibs/custom_types/cylinder.cpp',
      'clibs/tensors/D3Vector.cpp'
  ]}
]

import sys, os.path
if 'build' in sys.argv or ('install' in sys.argv and not os.path.exists('build')):
  cb.build(extensions, global_macros = global_macros, global_includes = global_includes)

import datetime
setup(
  name="pywat",
  version=datetime.date.today().strftime("%d%b%Y"),
  author="Joe Jordan",
  author_email="joe.jordan@imperial.ac.uk",
  url="TBA",
  packages=["pywat"]
)
```