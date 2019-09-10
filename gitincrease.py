#!/usr/local/bin/python3
import json
import subprocess
import os
import sys


dirpath = os.getcwd()
foldername = os.path.basename(dirpath)

def git_tag(p=''):
    if not p:
        p=dirpath
    proc = subprocess.Popen(['git','-C',p, 'describe','--tags','--abbrev=0'],stdout=subprocess.PIPE)
    for line in proc.stdout:
        line = line.rstrip().decode("utf-8")
    return line

def git_tag_add(v):
    v=v.split('.')
    mayor = v[0]
    minor = v[1]
    rev = v[2]
    rev=int(rev)+1
    return str(mayor) + '.' + str(minor) + '.' + str(rev)

def git_parent(d):
    if os.path.exists(d+'/.gitmodules'):
        return d
    else:
        if d ==  '/':
            return '/'
        return git_parent(os.path.dirname(d))

def git_commit_push_tag(d,version,comments):
    proc = subprocess.Popen(['git','-C', d, 'commit','-m',comments])
    proc.wait()
    proc = subprocess.Popen(['git','-C', d, 'tag',version])
    proc.wait()
    proc = subprocess.Popen(['git','-C', d, 'push'])
    proc.wait()
    proc = subprocess.Popen(['git','-C', d, 'push','--tags'])
    proc.wait()
    
def do_all(check_parent):    
    comments = input("Add comments ?\n")
    version=git_tag_add(git_tag(dirpath))

    meta = 'metadata.json'
    if os.path.exists(meta):
        with open(meta) as json_file:
            data = json.load(json_file)
        data['version'] = version    
    
        with open(meta,'w') as json_file:
            json.dump(data,json_file,indent=2)

    proc = subprocess.Popen(['git', 'add',meta])
    git_commit_push_tag(dirpath,version,comments)


    if check_parent:
        pdir=git_parent(dirpath)
        pversion = git_tag_add(git_tag(pdir))
        pcomment = '"updating ' + foldername + ' to version ' + version + '"'

        proc = subprocess.Popen(['git','-C', pdir, 'add',dirpath])
        proc.wait()
        git_commit_push_tag(pdir,pversion,pcomment)


    print("DONE!\n")


proc = subprocess.Popen(['git','-C', dirpath, 'status','-s'],stdout=subprocess.PIPE)
proc.wait()
line = proc.stdout.readline().decode("utf-8")
if len(sys.argv)==2:
    check_parent = 1
else:
    check_parent = 0

if line:
    do_all(check_parent)
else:
    print('nothing todo')