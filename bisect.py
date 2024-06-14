import os
import re
import pdb
import time
import logging
import tempfile
import subprocess

validate_map = {
    1: 'failed',
    0: 'succeed'
}


def subprocessRunCmd(cmd: str , cwd: str, timeout: int = None, obj: str = None):
    logging.debug("[Check]cmd: %s, %s" % (cmd, obj))
    proc = None
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


def RunCmd(cmd: str , cwd: str, timeout: int = None):
    try:
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, cwd=cwd)
        if proc.returncode == 0:
            return (proc.returncode, proc.stdout)
        return proc.returncode
    except subprocess.TimeoutExpired:
        return 999
    except Exception as e:
        return 999


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

def validate(revision, prog, option, oracle):
    comp_res, run_res, run_val = oracle
    obj_file = 'run.out'
    with tempfile.TemporaryDirectory() as tmp_dir:
        comp_cmd = f'{revision} {option} {prog} -o {obj_file}'
        comp_ret = RunCmd(comp_cmd, cwd=tmp_dir, timeout=10)
        comp_code = 0
        if isinstance(comp_ret, tuple):
            comp_code = comp_ret[0]
        else:
            comp_code = comp_ret
        if comp_code != comp_res:
            return 0
        else:
            if comp_res !=0:
                return 1
        
        run_ret = RunCmd('./run.out', cwd=tmp_dir, timeout=30)
        run_code, run_output = 0, 0
        if isinstance(run_ret, tuple):
            run_code = run_ret[0]
            run_output = run_ret[1].decode().strip()
        else:
            run_code = run_ret
        if run_code != run_res:
            return 0

        if run_output == run_val:
            return 1
        else:
            return 0


def start_serach(goodid, badid, gccgitcwd, prog, option, oracle):
    start_bisect_cmd = 'git bisect start --no-checkout'
    start_bisect_res = subprocessRunCmd(start_bisect_cmd, cwd=gccgitcwd, timeout=10, obj='startBisect')
    bisect_good_cmd = f'git bisect good {goodid}'
    bisect_good_res = subprocessRunCmd(bisect_good_cmd, cwd=gccgitcwd, timeout=10, obj='goodBisect')
    bisect_bad_cmd = f'git bisect bad {badid}'
    biscet_res = subprocessRunCmd(bisect_bad_cmd, cwd=gccgitcwd, timeout=30, obj='badBisect')
    biscet_res = biscet_res.decode()
    print(biscet_res, flush=True)

    hashid = ''
    pattern = r"\[(.*?)\]"
    match = re.search(pattern, biscet_res)
    if match:
        hashid = match.group(1)
    hashid = hashid[:7]
    revision = installRevision(hashid, gccgitcwd)
    validate_res = validate(f'{revision}/bin/gcc', prog, option, oracle)
    logging.info(f'revision {hashid} {validate_map[validate_res]} on test case {prog}')

    while True:
        bisect_cmd = ''
        if not validate_res:
            bisect_cmd = f'git bisect good {hashid}'
        else:
            bisect_cmd = f'git bisect bad {hashid}'
        biscet_res = subprocessRunCmd(bisect_cmd, cwd=gccgitcwd, timeout=10, obj='Bisect')
        biscet_res = biscet_res.decode()
        print(biscet_res, flush=True)
        match = re.search(pattern, biscet_res)
        if match:
            hashid = match.group(1)
        hashid = hashid[:7]
        if 'is the first bad commit' in biscet_res:
            first_line = biscet_res.splitlines()[0]
            hashid = first_line.split()[0]
            hashid = hashid[:7]
            break
        revision = installRevision(hashid, gccgitcwd)
        validate_res = validate(f'{revision}/bin/gcc', prog, option, oracle)
        logging.info(f'revision {hashid} {validate_map[validate_res]} on test case {prog}')

    revision = installRevision(hashid, gccgitcwd)
    validate_res = validate(f'{revision}/bin/gcc', prog, option, oracle)
    logging.info(f'revision {hashid} {validate_map[validate_res]} on test case {prog}')
    if validate_res:
        print(f'find the first bad commit: {hashid}', flush=True)

    reset_bisect_cmd = 'git bisect reset'
    subprocessRunCmd(reset_bisect_cmd, cwd=gccgitcwd, timeout=10, obj='resetBisect')


if __name__ == "__main__":
    gccgitcwd='/root/gcc-git' ### your gcc git repository cloned

    source_filename = os.path.join(os.getcwd() + '114551.c') ### source code of gcc bug 114551
    wrong_behavior = (0, 139, 0) ### (compilation return code, execution return code, execution output)

    good_commit, bad_commit = '48f0f29', '3d48c11'
    
    logging.basicConfig(filename="bisect_test.log", level=logging.INFO)
    start_serach(good_commit, bad_commit, gccgitcwd, source_filename, '-O3', wrong_behavior)
    # ret = validate('/usr/local/gccrev/48f0f29', '/root/114551.c', '-O3', (139,0,0))
    # print(ret)
