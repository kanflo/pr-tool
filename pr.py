#!/usr/bin/env python

"""
A simple tool for listing and fetching github pull requests
Usaeg: cd <cloned git>
pr.py -l

"""
import requests
import sys
from subprocess import PIPE, Popen

"""
Extract github short url from git in current directory
If git remote -v says
origin   git@github.com:kanflo/pr-tool.git (fetch)
return kanflo/pr-tool
"""
def github_url():
    p = Popen(["git", "remote", "-v"], stdout = PIPE, stderr = PIPE)
    (stdoutdata, stderrdata) = p.communicate()
    if "Not a git repository" in stderrdata:
        print("Not a git repo")
        return None

    if not "github.com" in stdoutdata:
        print("Not a GitHub repo")
        return None

    lines = stdoutdata.split('\n')
    url = lines[0]
    start = url.find("github.com:")
    end = url.find(".git")
    return url[start+11 : end]

"""
List pull requests
"""
def list_pull_requests(url):
    r = requests.get('https://api.github.com/repos/%s/pulls' % url)
    if r.status_code != 200:
        print("GitHub returned %s" % r.status_code)
        return None
    else:
        return r.json()


def checkout_pr(pr):
    n = pr['number']
    p = Popen(["git", "fetch", "origin", "pull/%s/head:pr_%s" % (n, n)], stdout = PIPE, stderr = PIPE)
    (stdoutdata, stderrdata) = p.communicate()
    if not "new ref" in stderrdata:
        print(stderrdata.strip())
        return False
 
    p = Popen(["git", "checkout", "pr_%s" % (n)], stdout = PIPE, stderr = PIPE)
    (stdoutdata, stderrdata) = p.communicate()
    if not "Switched to branch" in stderrdata:
        print(stderrdata.strip())
        return False

    return True


# main!
if len(sys.argv) == 1:
    print("Usage: %s [-l] [-c <id>]" % sys.argv[0])
    sys.exit(0)

url = github_url()
if url:
    if sys.argv[1] == "--list" or sys.argv[1] == "-l":
        prs = list_pull_requests(url)
        if len(prs) == 0:
            print("No pull requests")
        else:
            for pr in prs:
                print(" %10s  %3s   %s" % (pr['user']['login'], pr['number'], pr['title']))
#            print("%s" % (pr['body'].strip()))
    if sys.argv[1] == "--check-out" or sys.argv[1] == "-c":
        pr_id = int(sys.argv[2])
        prs = list_pull_requests(url)
        if len(prs) == 0:
            print("No pull requests")
        else:
            found = False
            for pr in prs:
                if int(pr['number']) == pr_id:
                    found = True
                    checkout_pr(pr)
            if not found:
                print("PR %d not found." % pr_id)
