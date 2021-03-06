#!/usr/bin/python

import os
import shutil
import signal
import string
import subprocess
import sys
from distutils.spawn import find_executable


def findparentfiles(fname):
    filelist = []
    newlist = []
    args = ['grep', '-rl', '--exclude-dir=.git', fname]
    proc = subprocess.Popen(args,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            universal_newlines=False,
                            preexec_fn=lambda:
                            signal.signal(signal.SIGPIPE, signal.SIG_DFL))
    data = proc.communicate()[0]
    if proc.returncode != 0:
        return filelist
    for filename in data.splitlines():
        if filename.endswith('.yaml') and '/' not in filename:
            filelist.append(filename)
        else:
            newlist = findparentfiles(filename)
            for tempname in newlist:
                filelist.append(tempname)
    return filelist


jjb_cmd = find_executable('jenkins-jobs') or sys.exit('jenkins-jobs is not found.')
jjb_args = [jjb_cmd]

jjb_user = os.environ.get('JJB_USER')
jjb_password = os.environ.get('JJB_PASSWORD')
if jjb_user is not None and jjb_password is not None:
    jenkins_jobs_ini = ('[job_builder]\n'
                        'ignore_cache=True\n'
                        'keep_descriptions=False\n'
                        '\n'
                        '[jenkins]\n'
                        'user=%s\n'
                        'password=%s\n'
                        'url=https://ci.linaro.org/\n' % (jjb_user, jjb_password))
    with open('jenkins_jobs.ini', 'w') as f:
        f.write(jenkins_jobs_ini)
    jjb_args.append('--conf=jenkins_jobs.ini')

jjb_args.extend(['update', 'template.yaml'])

try:
    git_args = ['git', 'diff', '--name-only',
                os.environ.get('GIT_PREVIOUS_COMMIT'),
                os.environ.get('GIT_COMMIT')]
    proc = subprocess.Popen(git_args,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            universal_newlines=False,
                            preexec_fn=lambda:
                            signal.signal(signal.SIGPIPE, signal.SIG_DFL))
except (OSError, ValueError) as e:
    raise ValueError("%s" % e)

data = proc.communicate()[0]
if proc.returncode != 0:
    raise ValueError("command has failed with code '%s'" % proc.returncode)

filelist = []
files = []
for filename in data.splitlines():
    if filename.endswith('.yaml') and '/' not in filename:
        filelist.append(filename)
    else:
        files = findparentfiles(filename)
        for tempname in files:
            filelist.append(tempname)

# Remove dplicate entries in the list
filelist = list(set(filelist))

for conf_filename in filelist:
    with open(conf_filename) as f:
        buffer = f.read()
        template = string.Template(buffer)
        buffer = template.safe_substitute(
            AUTH_TOKEN=os.environ.get('AUTH_TOKEN'),
            LT_QCOM_KEY=os.environ.get('LT_QCOM_KEY'),
            LAVA_USER=os.environ.get('LAVA_USER'),
            LAVA_TOKEN=os.environ.get('LAVA_TOKEN'))
        with open('template.yaml', 'w') as f:
            f.write(buffer)
        try:
            proc = subprocess.Popen(jjb_args,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    universal_newlines=False,
                                    preexec_fn=lambda:
                                    signal.signal(signal.SIGPIPE, signal.SIG_DFL))
        except (OSError, ValueError) as e:
            raise ValueError("%s" % e)

        data = proc.communicate()[0]
        if proc.returncode != 0:
            raise ValueError("command has failed with code '%s'" % proc.returncode)

        os.remove('template.yaml')
        #shutil.rmtree('out')

if os.path.exists('jenkins_jobs.ini'):
    os.remove('jenkins_jobs.ini')
