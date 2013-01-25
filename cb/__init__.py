# Complicated Build (cb) Copyright (c) 2013 Joe Jordan
# This code is licensed under MIT license (see LICENSE for details)
#

from distutils.sysconfig import get_python_inc
import sys, os, os.path, shutil, re

final_prefix = 'build' + os.sep + 'lib' + os.sep
temp_prefix = 'build' + os.sep + 'cb_temp' + os.sep

# add more file extensions, with appropriate compiler command, here:
# be warned that you may need to customise _linker_vars below too.
compiler = {
  'cpp' : 'g++',
  'c' : 'gcc',
  'f90' : 'gfortran'
}

cythonize = None

def _custom_cythonise(files):
  global cythonize
  for i, f in enumerate(files):
    if os.path.split(f)[1].split('.')[1] == "pyx":
      if cythonize == None:
        from Cython.Build import cythonize
      e = cythonize(f)[0]
      files[i] = e.sources[0]

def _ensure_dirs(*args):
  for d in args:
    try:
      os.makedirs(d)
    except OSError:
      # we don't care if the containing folder already exists.
      pass

def _final_target(name):
  return final_prefix + name.replace('.', os.sep) + '.so'

def _temp_dir_for_seperate_module(name, arch):
  return temp_prefix + name.replace('.', '') + arch + os.sep

def _macro_string(macros):
  if macros == None or len(macros) == 0:
    return ""
  outs = []
  for m in macros:
    try:
      outs.append("-D" + m[0] + '=' + m[1])
    except:
      outs.append("-D" + m[0])
  return ' '.join(outs)

def _include_string(includes):
  if includes == None or len(includes) == 0:
    return ""
  outs = []
  for i in includes:
    outs.append("-I" + i)
  return ' '.join(outs)

source_to_object_re = re.compile('[.' + os.sep + ']')
def _source_to_object(f):
  return source_to_object_re.sub('', f) + '.o'

def _linker_vars(file_exts):
  linking_compiler = compiler['c']
  file_exts = set(file_exts)
  runtime_libs = ""
  if 'cpp' in file_exts:
    linking_compiler = compiler['cpp']
  if 'f90' in file_exts:
    if linking_compiler == compiler['cpp']:
      runtime_libs = "-lc -lstdc++"
    linking_compiler = compiler['f90']
  return (linking_compiler, runtime_libs)

def _exists_and_newer(target, source):
  if os.path.exists(target) and min([target, source], key=os.path.getmtime) == source:
    return True
  return False

def _run_command(c, err="compiler error detected!"):
  print c
  if os.system(c) != 0:
    print err
    exit()

def _seperate_build(extension, global_macros, global_includes):
  target = _final_target(extension['name'])
  temp = _temp_dir_for_seperate_module(extension['name'], extension['arch'])
  _ensure_dirs(os.path.split(target)[0], temp)
  _custom_cythonise(extension['sources'])
  compile_commands = []
  file_exts = []
  object_files = []
  global_macros = _macro_string(global_macros)
  global_includes = _include_string(global_includes)
  
  # compute the compile line for each file:
  for f in extension['sources']:
    file_exts.append(os.path.split(f)[1].split('.')[1])
    object_files.append(temp + _source_to_object(f))
    compile_commands.append(
      ' '.join([
        compiler[file_exts[-1]],
        global_macros,
        _macro_string(extension['define_macros']) if 'define_macros' in extension else "",
        "-arch", extension['arch'],
        global_includes,
        _include_string(extension['include_dirs']) if 'include_dirs' in extension else "",
        '-o', object_files[-1],
        '-c', f
      ])
    )
  
  # penultimately, we compute the linking line:
  linking_compiler, runtime_libs = _linker_vars(file_exts)
  link_command = ' '.join([
    linking_compiler,
    "-arch", extension['arch'],
    runtime_libs,
    "-bundle -undefined dynamic_lookup", # magic python .so things...
    ' '.join(object_files),
    '-o', target
  ])
  
  # now actually run the commands, if the object files need refreshing:
  compiled_something = False
  for i, cc in enumerate(compile_commands):
    if _exists_and_newer(object_files[i], extension['sources'][i]):
      print "skipping ", extension['sources'][i], "is already up to date."
      continue
    compiled_something = True
    _run_command(cc)
  
  if os.path.exists(target) and not compiled_something:
    print "module", extension['name'], "was all up to date."
    return
  _run_command(link_command, "linker error detected!")  

def _common_build(extensions, global_macros, global_includes, arch):
  targets = [_final_target(e['name']) for e in extensions]
  temp = temp_prefix + "common_build" + arch + os.sep
  
  _ensure_dirs(*([os.path.split(t)[0] for t in targets] + [temp]))
  
  # build a common pool of sources:
  sources = []
  for e in extensions:
    # may result in cythonizing the same file mulitple times, but we need to keep track of which
    # extension contains which file types, so this is fiddly to avoid.
    _custom_cythonise(e['sources'])
    sources += e['sources']
  sources = list(set(sources))
  
  compile_commands = []
  file_exts = []
  object_files = []
  global_macros = _macro_string(global_macros)
  global_includes = _include_string(global_includes)
  
  # generate the compile lines for them:
  for f in sources:
    file_exts.append(os.path.split(f)[1].split('.')[1])
    object_files.append(temp + _source_to_object(f))
    compile_commands.append(
      ' '.join([
        compiler[file_exts[-1]],
        global_macros,
        "-arch", arch,
        global_includes,
        '-o', object_files[-1],
        '-c', f
      ])
    )
  
  # generate a list of linker lines:
  linker_lines = []
  for i, e in enumerate(extensions):
    # for each linker line, we have to choose the correct set of file extensions.
    linking_compiler, runtime_libs = _linker_vars([os.path.split(f)[1].split('.')[1] for f in e['sources']])
    linker_lines.append(' '.join([
      linking_compiler,
      "-arch", arch,
      runtime_libs,
      "-bundle -undefined dynamic_lookup", # magic python .so things...
      ' '.join([temp + _source_to_object(f) for f in e['sources']]),
      '-o', targets[i]
    ]))
    
  # run everything.
  compiled_something = False
  for i, cc in enumerate(compile_commands):
    if _exists_and_newer(object_files[i], sources[i]):
      print "skipping ", sources[i], "is already up to date."
      continue
    compiled_something = True
    _run_command(cc)
  
  # if ANY source files have changed, run all linker lines.
  if all([os.path.exists(t) for t in targets]) and not compiled_something:
    print "all modules already up to date."
    return
  
  for cc in linker_lines:
    _run_command(cc, "linker error detected!")

def build(extensions, arch='x86_64', global_macros=None, global_includes=None):
  """extensions should be an array of dicts containing:
  {
    'name' : 'mylib.mymodule',
    'sources' : [
      'path/to/source1.cpp',
      'path/to/source2.f90',
      'path/to/source3.pyx',
      'path/to/source4.c'
    ],
    # optional:
    'include_dirs' : ['paths'],
    'define_macros' : [("MACRO_NAME", "VALUE")] # or just ("MACRO_NAME",) but remember the ,!
  }
  if global_macros is provided, and 'define_macros' and 'include_dirs' is missing
  for all extensions, common sources will only be built once, and linked multiple times.
  note, you may still declare global_macros and global_includes.
  """
  if global_includes == None:
    global_includes = [get_python_inc()]
  else:
    global_includes = [get_python_inc()] + global_includes
  if (len(extensions) > 1 and 
    all(['define_macros' not in e and 'include_dirs' not in e for e in extensions])):
    _common_build(extensions, global_macros, global_includes, arch)
  else:
    for e in extensions:
      e['arch'] = arch
      _seperate_build(e, global_macros, global_includes)
  
