import os
import time
import logging
import subprocess


def subprocessRunCmd(cmd: str , cwd: str, timeout: int = None, obj: str = None):
    logging.debug("[Check]cmd: %s, %s" % (cmd, obj))
    proc = None ### the subprocess
    try:
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, cwd=cwd)
        if proc.returncode == 0:
            return proc.stdout

        logging.debug("[Check]Exception: %s with returncode of %s" % (proc.stderr.decode(), proc.returncode))
        raise Exception('ERROR' + obj + '-' + str(proc.returncode))
    except subprocess.TimeoutExpired:
        raise Exception('TIMEOUT' + obj)
    except Exception as e:
        logging.error('[Check]Exception %s for %s' % (str(e), cmd))
        if proc is None:
            raise Exception('ERROR' + obj)
        else:
            raise Exception('ERROR' + obj + '-' + str(proc.returncode))


def installRevision(revision, gccgitcwd):
    if os.path.exists(f'/usr/local/gccrev/{revision}'):
        logging.info(f'{revision} is already installed!')
        return

    stime = time.time()
    buildrcwd = os.path.join(os.getcwd(), f'buildgcc{revision}')
    out = subprocessRunCmd(f'git checkout {revision}', cwd=gccgitcwd, obj=f'check out for {revision}')
    logging.info(f'check out for {revision}')

    out = subprocessRunCmd('./contrib/download_prerequisites', cwd=gccgitcwd, obj=f'download prerequisites for {revision}')
    logging.info(f'download prerequisites for {revision}')

    if os.path.exists(buildrcwd):
        subprocessRunCmd(f'rm -r {buildrcwd}', cwd=os.getcwd(), obj=f'rm -r {buildrcwd}')
        logging.info(f'rm -r {buildrcwd}')
    
    out = subprocessRunCmd(f'mkdir {buildrcwd}', cwd=os.getcwd(), obj=f'mkdir {buildrcwd}')
    logging.info(f'mkdir {buildrcwd}')
    
    out = subprocessRunCmd(f'{gccgitcwd}/configure --disable-multilib --disable-bootstrap --enable-languages=c,c++ --prefix=/usr/local/gccrev/{revision}', cwd=buildrcwd, obj=f'configure: {revision}')
    logging.info(f'configure: {revision}')

    try:
        out = subprocessRunCmd(f'make -j 40', cwd=buildrcwd, obj=f'make {revision}')
        logging.info(f'make {revision}')
    except Exception:
        logging.error(f'stdout: {out.stdout}')
        logging.error(f'stderr: {out.stderr}')
        logging.info(f'Failed to install {revision}!')
        return

    try:    
        out = subprocessRunCmd(f'make install-strip', cwd=buildrcwd, obj=f'install {revision}')
        logging.info(f'install {revision}')
    except Exception:
        logging.error(f'stdout: {out.stdout}')
        logging.error(f'stderr: {out.stderr}')
        logging.info(f'Failed to install {revision}!')
        return

    subprocessRunCmd(f'rm -r {buildrcwd}', cwd=os.getcwd(), obj=f'rm -r {buildrcwd}')
    logging.debug(f'rm -r {buildrcwd}')

    logging.info(f'install {revision} spend: {time.time() - stime}, seconds')

if __name__ == "__main__":
    ### please first clone the repository using the following command, the repository will be in the gcc-git directory
    ### git clone git://gcc.gnu.org/git/gcc.git
    gccgitcwd = os.path.join(os.getcwd(), 'gcc-git')

    logging.basicConfig(filename="install.log", level=logging.INFO)
    installRevision('48a320a', gccgitcwd) ### install gcc 15.0.0
    installRevision('48f0f29', gccgitcwd) ### install gcc 14.0.0
    installRevision('091e102', gccgitcwd) ### install gcc 13.0.0
    installRevision('0cc7933', gccgitcwd) ### install gcc 12.0.0
    installRevision('46eed41', gccgitcwd) ### install gcc 11.0.0
    installRevision('68ec60c', gccgitcwd) ### install gcc 10.0.0
