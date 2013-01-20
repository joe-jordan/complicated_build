complicated_build
=================

a python extension build system (with Cython support) which allows automated compilation a mixture of C, C++, FORTRAN and Cython sources without F2PY interference.

example usage in a setup.py:

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


or, a more involved example:

    import cb
    from distutils.core import setup
    import numpy as np
    
    global_includes = [np.get_include()]
    global_macros = [("__FORCE_CPP__",)]
    
    extensions = [
      {'name' : 'watershed',
        'sources' : [
          'pywat/watershed.pyx',
          'clibs/watershed.cpp',
          'clibs/stripack.f90',
          'clibs/tensors/D3Vector.cpp'
      ]},
      {'name' : 'shapes',
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