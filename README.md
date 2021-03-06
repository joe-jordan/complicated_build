complicated_build
=================

(released under the MIT license, see the LICENSE file.)

a python extension build system (with Cython support) which allows automated compilation a mixture of C, C++, FORTRAN and Cython sources without F2PY interference.

*NEW IN v1.4:* support for specifying library locations (only globally.)

*NEW IN v1.3:* support for linking against static libs on a per-extension basis. see new 'link_to' key on extension dicts.

inspired by the problem in [this stackoverflow question](http://stackoverflow.com/questions/12696520/cython-and-fortran-how-to-compile-together-without-f2py).

Note, this library also provides a significant improvement on the default python build system for native extensions with many source files: by default it *caches all temporary build objects*, and only recompiles the particular source files that have changed. The distutils default (designed for single file extensions, no doubt) recompiles *all* sources if *any* have changed. When debugging extensions, e.g. making small changes to one or two source files in a long list, this can present a significant time saving in each build/run cycle.

*SUBNOTE:* There is also a minor 'bug' in that, since you don't specify header files like in a `Makefile`, it doesn't detect changes in header files. If this is annoying enough please post a bug, and I'll work out how to fix it without breaking the existing interface (which will be a minor pain).

This module uses the *default python flags* for building sources, which includes all kinds of cruft that were generated in the makefile that compiled python itself. Also, the `arch` argument is no longer passed to the compiler, as this is not compatible with some compilers, and is now only used in temp directory names. (if such a flag is required, it will be present in the `distutils.sysconfig` vars without further intervention.)

note, finally, that this has been modified to act as a decorator for `distutils.core.setup`, see the examples of the new invocation style below.

example usage in a setup.py:

```python
import cb

global_includes = ['/opt/local/include']
global_lib_dirs = ['/opt/local/lib']
global_macros = [("__SOME_MACRO__",), ("__MACRO_WITH_VALUE__", "5")]

extensions = [{'name' : 'mylib.impl',
    'sources' : ['mylib/impl.pyx', 'clibs/some_other_code.cpp'],
    'link_to' : ["pthread"] # will include the -l when added to the linker line.
}]

import datetime
cb.setup(extensions, global_macros = global_macros, global_includes = global_includes, 
  global_lib_dirs = global_lib_dirs)(
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
  'cpp' : " ".join(distutils.sysconfig.get_config_vars('CXX', 'CPPFLAGS')), # normally something like g++
  'c' : " ".join(distutils.sysconfig.get_config_vars('CC', 'CFLAGS')), # normally something like gcc
  'f90' : 'gfortran'
}
```

*(sysconfig functions return what was in the Makefile that built python.)*

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
cb.compiler['cxx'] = cb.compiler['cpp']
```

however, you may need to modify the function `cb._linker_vars` to better reflect what runtimes you need to link against (especially if you are mixing fortran and C++ sources.)

additionally, if you don't have Cython installed on your system, the program shouldn't crash (unless you're trying to compile `.pyx` files, of course) -- it only gets around to `import`ing Cython when it needs to `cythonize` the sources.

Finally, a more involved example:

```python
import cb
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

import datetime
cb.setup(extensions, global_macros = global_macros, global_includes = global_includes)(
  name="pywat",
  version=datetime.date.today().strftime("%d%b%Y"),
  author="Joe Jordan",
  author_email="joe.jordan@imperial.ac.uk",
  url="TBA",
  packages=["pywat"]
)
```

**INDEPENDENCE**

If you don't want your project to require the user to come and find my library and install it, you can bundle it with your software as follows:

```python
try:
  import cb
except ImportError:
  print "downloading complicated build..."
  import urllib2
  response = urllib2.urlopen('https://raw.github.com/joe-jordan/complicated_build/master/cb/__init__.py')
  content = response.read()
  f = open('cb.py', 'w')
  f.write(content)
  f.close()
  import cb
  print "done!"
```

You can see this setup in action in one of my other projects, [pyvoro](https://github.com/joe-jordan/pyvoro), the snippet is simply included in the top of [setup.py](https://github.com/joe-jordan/pyvoro/blob/master/setup.py)
