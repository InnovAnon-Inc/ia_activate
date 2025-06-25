#! /usr/bin/env python
# cython: language_level=3
# distutils: language=c++

"""Python port: <venv>/bin/activate"""

import asyncio
from asyncio            import AbstractEventLoop
from contextlib         import asynccontextmanager, contextmanager
from functools          import partial, wraps
import inspect
import logging
import os
from pathlib            import Path
import subprocess
from subprocess         import CalledProcessError
import sys
from typing             import Optional
from typing             import *
from typing             import ParamSpec
from typing_extensions import AsyncGenerator

import aioshutil
import aiofiles
import structlog

from ia_typ import P, T, Decorator, Function, Wrapper
from ia_is_venv import is_venv
from ia_get_default_shell import get_default_shell

logger = structlog.get_logger()

def activated(venv_dir:Path)->Decorator:
    def decorator(func:Function)->Wrapper:
        async def awrapper(*args:P.args, **kwargs:P.kwargs)->T:
            with activate(venv_dir):
                return await func(*args, **kwargs)
        if inspect.iscoroutinefunction(func):
            return awrapper
        def wrapper(*args:P.args, **kwargs:P.kwargs)->T:
            async with aactivate(venv_dir):
                return func(*args, **kwargs)
        return wrapper
    return decorator

@contextmanager
def activate(venv_dir:Path, )->Generator[None,None]:
    logger.debug('activate(venv_dir=%s)', venv_dir, )
    _activate(venv_dir, )
    try:
        yield
    finally:
        deactivate()

@asynccontextmanager
async def aactivate(venv_dir:Path, )->AsyncGenerator[None,None]:
    await logger.adebug('activate(venv_dir=%s)', venv_dir, )
    await _aactivate(venv_dir, )
    try:
        yield
    finally:
        await adeactivate()

def _activate(venv_dir:Path,)->None:
    # This file must be used with "source bin/activate" *from bash*
    # You cannot run it directly
    logger.info('_activate(venv_dir=%s)', venv_dir, )

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
    assert is_venv()

def deactivate(nondestructive:bool=False,)->None:
    """ reset old environment variables """

    logger.info('deactivate(nondestructive=%s)', nondestructive, )

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

    assert(not is_venv())
    #if [ ! "${1:-}" = "nondestructive" ] ; then
    ## Self destruct!
    #    unset -f deactivate
    #fi
    if nondestructive:
        return

    #del globals()['deactivate']

async def _aactivate(venv_dir:Path,)->None:
    await logger.ainfo('_activate(venv_dir=%s)', venv_dir, )

    await adeactivate(nondestructive=True,)

    assert await aiofiles.os.path.isdir(venv_dir)
    os.setenv('VIRTUAL_ENV', str(venv_dir)) # TODO

    path :str = os.getenv('PATH', '')
    pathl:List[str] = os.pathsep.split(path)
    prepend_path:str = venv_dir / 'bin'
    assert await aiofiles.os.path.isdir(prepend_path)
    pathl.insert(0, prepend_path)
    path = os.pathsep.join(pathl)
    os.setenv('PATH', path)

    pythonhome:str = os.getenv('PYTHONHOME', '')
    if pythonhome:
        os.environ['_OLD_VIRTUAL_PYTHONHOME'] = pythonhome
        os.unsetenv('PYTHONHOME')

    virtual_env_disable_prompt:str = os.getenv('VIRTUAL_ENV_DISABLE_PROMPT', '')
    if(not virtual_env_disable_prompt):
        ps1:str = os.getenv('PS1', '')
        os.environ['_OLD_VIRTUAL_PS1'] = ps1
        virtual_env_prompt:str = '(venv) '
        os.setenv('VIRTUAL_ENV_PROMPT', virtual_env_prompt)
        ps1 = virtual_env_prompt + ps1
        os.setenv('PS1', ps1)

    assert is_venv()

def adeactivate(nondestructive:bool=False,)->None:
    """ reset old environment variables """

    await logger.ainfo('deactivate(nondestructive=%s)', nondestructive, )

    old_virtual_path:str = os.getenv('_OLD_VIRTUAL_PATH', '')
    if old_virtual_path:
        os.setenv('PATH', old_virtual_path)
        os.unsetenv('_OLD_VIRTUAL_PATH')

    old_virtual_pythonhome:str = os.getenv('_OLD_VIRTUAL_PYTHONHOME', '')
    if old_virtual_pythonhome:
        os.setenv('PYTHONHOME', old_virtual_pythonhome)
        os.unsetenv(old_virtual_pythonhome)

    old_virtual_ps1:str = os.getenv('_OLD_VIRTUAL_PS1', '')
    if old_virtual_ps1:
        os.setenv('PS1', old_virtual_ps1)
        os.unsetenv('_OLD_VIRTUAL_PS1')
    
    os.unsetenv('VIRTUAL_ENV')
    os.unsetenv('VIRTUAL_ENV_PROMPT')

    assert(not is_venv())
    if nondestructive:
        return

    #del globals()['adeactivate']

@activated(Path() / 'venv')
async def main()->None:
    assert is_venv()
    shell:str       = await get_default_shell()
    assert await aioshutil.which(shell)
    args :List[str] = [shell, shell, '-i']
    os.execl(*args)

if __name__ == '__main__':
    asyncio.run(main())
