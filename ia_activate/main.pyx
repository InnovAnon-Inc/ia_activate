#! /usr/bin/env python
# cython: language_level=3
# distutils: language=c++

""" Activate venv """

from contextlib import contextmanager
import os
from pathlib                                 import Path
from typing                                  import List, Optional, Tuple

from structlog                               import get_logger

from ia_check_venv.main                      import check_venv
from ia_check_venv.main                      import verify_venv

logger = get_logger()

#def redirect_virtual_env(venv_dir:Path,)->str:
#	logger.debug('(redirect_virtual_env) env dir: %s', venv_dir)
#	assert venv_dir.is_dir()
#	assert(not check_venv())
#
#	virtual_env:Optional[str] = os.getenv('VIRTUAL_ENV')
#	assert(virtual_env is None)
#
#	virtual_env:str           = str(venv_dir.resolve())
#	logger.debug('(redirect_virtual_env) virtual env: %s', virtual_env)
#
#	#os.putenv('VIRTUAL_ENV', virtual_env)
#	os.environ['VIRTUAL_ENV'] = virtual_env
#	assert(os.environ['VIRTUAL_ENV'] == virtual_env)
#	return virtual_env
#
#def prepend_path(bin_path:Path,)->str:
#	logger.debug('(prepend_path) bin path: %s', bin_path)
#	assert bin_path.is_dir()
#	#assert(not check_venv())
#
#	path       :str           = os.environ['PATH']
#	#assert(str(bin_path) not in path)
#	logger.debug('(prepend_path) path: %s', path)
#
#	paths      :List[str]     = [str(bin_path), path,]
#	path                      = os.pathsep.join(paths)
#	logger.debug('(prepend_path) new path: %s', path)
#
#	#os.putenv('PATH', path)
#	os.environ['PATH'] = path
#	assert(os.environ['PATH'] == path)
#	return path
#
#def redirect_executable(bin_path:Path,)->str:
#	logger.debug('(redirect_executable) redirect executable: %s', bin_path)
#	assert bin_path.is_dir()
#	#assert(not check_venv())
#
#	_executable :Path         = bin_path / 'python'
#	assert _executable.is_file()
#
#	executable  :str          = str(_executable.resolve())
#	logger.debug('(redirect_executable) sys executable: %s', sys.executable)
#
#	sys.executable            = executable
#	logger.debug('(redirect_executable) new executable: %s', sys.executable)
#
#	return executable
#
#def _activate(venv_dir:Path,)->None:
#	logger.debug('(enter_venv) env dir: %s', venv_dir)
#	assert(not check_venv())
#
#	virtual_env:str           = redirect_virtual_env(venv_dir=venv_dir,)
#	sys.prefix                = virtual_env
#
#	bin_path   :Path          = Path(sys.prefix) / 'bin'
#	prepend_path(bin_path=bin_path,)
#
#	executable :str           = redirect_executable(bin_path=bin_path,)
#	logger.debug('(enter_venv) executable: %s', executable)
#
#	logger.debug('(enter_venv) environ: %s', os.environ)
#	logger.debug('(enter_venv) argv %s', sys.argv)
#	logger.debug('(enter_venv) before exec')

@contextmanager
def activate(venv_dir:Path,)->None:
	_activate()
	yield
	deactivate()

def _activate(venv_dir:Path,)->None:
	# This file must be used with "source bin/activate" *from bash*
	# You cannot run it directly

	# unset irrelevant variables
	#deactivate nondestructive
	deactivate(nondestructive=True,)

	# on Windows, a path can contain colons and backslashes and has to be converted:
	#if [ "${OSTYPE:-}" = "cygwin" ] || [ "${OSTYPE:-}" = "msys" ] ; then
	#    # transform D:\path\to\venv to /d/path/to/venv on MSYS
	#    # and to /cygdrive/d/path/to/venv on Cygwin
	#    export VIRTUAL_ENV=$(cygpath "/home/frederick/venv")
	#else
	#    # use the path as-is
	#    export VIRTUAL_ENV="/home/frederick/venv"
	#fi
	assert venv_dir.is_dir()
	os.setenv('VIRTUAL_ENV', str(venv_dir)) # TODO

	#_OLD_VIRTUAL_PATH="$PATH"
	#PATH="$VIRTUAL_ENV/bin:$PATH"
	#export PATH
	path :str = os.getenv('PATH', '')
	pathl:List[str] = os.pathsep.split(path)
	prepend_path:str = venv_dir / 'bin'
	assert Path(prepend_path).is_dir()
	pathl.insert(0, prepend_path)
	path = os.pathsep.join(pathl)
	os.setenv('PATH', path)

	# unset PYTHONHOME if set
	# this will fail if PYTHONHOME is set to the empty string (which is bad anyway)
	# could use `if (set -u; : $PYTHONHOME) ;` in bash
	#if [ -n "${PYTHONHOME:-}" ] ; then
	#    _OLD_VIRTUAL_PYTHONHOME="${PYTHONHOME:-}"
	#    unset PYTHONHOME
	#fi
	pythonhome:str = os.getenv('PYTHONHOME', '')
	if pythonhome:
		os.environ['_OLD_VIRTUAL_PYTHONHOME'] = pythonhome
		os.unsetenv('PYTHONHOME')

	#if [ -z "${VIRTUAL_ENV_DISABLE_PROMPT:-}" ] ; then
	#    _OLD_VIRTUAL_PS1="${PS1:-}"
	#    PS1="(venv) ${PS1:-}"
	#    export PS1
	#    VIRTUAL_ENV_PROMPT="(venv) "
	#    export VIRTUAL_ENV_PROMPT
	#fi
	virtual_env_disable_prompt:str = os.getenv('VIRTUAL_ENV_DISABLE_PROMPT', '')
	if(not virtual_env_disable_prompt):
		ps1:str = os.getenv('PS1', '')
		os.environ['_OLD_VIRTUAL_PS1'] = ps1
		virtual_env_prompt:str = '(venv) '
		os.setenv('VIRTUAL_ENV_PROMPT', virtual_env_prompt)
		ps1 = virtual_env_prompt + ps1
		os.setenv('PS1', ps1)

	# Call hash to forget past commands. Without forgetting
	# past commands the $PATH changes we made may not be respected
	#hash -r 2> /dev/null
	assert check_venv()

def deactivate(nondestructive:bool=False,)->None:
	""" reset old environment variables """

	#if [ -n "${_OLD_VIRTUAL_PATH:-}" ] ; then
	#    PATH="${_OLD_VIRTUAL_PATH:-}"
	#    export PATH
	#    unset _OLD_VIRTUAL_PATH
	#fi
	old_virtual_path:str = os.getenv('_OLD_VIRTUAL_PATH', '')
	if old_virtual_path:
		os.setenv('PATH', old_virtual_path)
		os.unsetenv('_OLD_VIRTUAL_PATH')

	#if [ -n "${_OLD_VIRTUAL_PYTHONHOME:-}" ] ; then
	#    PYTHONHOME="${_OLD_VIRTUAL_PYTHONHOME:-}"
	#    export PYTHONHOME
	#    unset _OLD_VIRTUAL_PYTHONHOME
	#fi
	old_virtual_pythonhome:str = os.getenv('_OLD_VIRTUAL_PYTHONHOME', '')
	if old_virtual_pythonhome:
		os.setenv('PYTHONHOME', old_virtual_pythonhome)
		os.unsetenv(old_virtual_pythonhome)

	# Call hash to forget past commands. Without forgetting
	# past commands the $PATH changes we made may not be respected
	#hash -r 2> /dev/null

	#if [ -n "${_OLD_VIRTUAL_PS1:-}" ] ; then
	#    PS1="${_OLD_VIRTUAL_PS1:-}"
	#    export PS1
	#    unset _OLD_VIRTUAL_PS1
	#fi
	old_virtual_ps1:str = os.getenv('_OLD_VIRTUAL_PS1', '')
	if old_virtual_ps1:
		os.setenv('PS1', old_virtual_ps1)
		os.unsetenv('_OLD_VIRTUAL_PS1')
    
	#unset VIRTUAL_ENV
	#unset VIRTUAL_ENV_PROMPT
	os.unsetenv('VIRTUAL_ENV')
	os.unsetenv('VIRTUAL_ENV_PROMPT')

	assert(not check_venv())
	#if [ ! "${1:-}" = "nondestructive" ] ; then
	## Self destruct!
	#    unset -f deactivate
	#fi
	if nondestructive:
		return

	raise NotImplementedError() # TODO

def exec_shell()->None:
	shell   :str  = os.environ['SHELL']
	os.execle(shell, shell, '-l', os.environ,)

def main()->None:
	if check_venv():
		logger.info('already in venv')
		return
	assert(not check_venv())
	venv_dir:Path = Path()
	assert venv_dir.is_dir()

	with activate(env_dir=venv_dir,) as _:
		assert check_venv()
		pid:int = os.fork()
		assert check_venv()
		if(pid != 0):    # parent
			return   # exit immediately
		assert(pid == 0) # child
		exec_shell()
	assert(not check_venv())

if __name__ == '__main__':
	main()

__author__:str = 'you.com' # NOQA



