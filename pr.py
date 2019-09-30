#!/usr/bin/env python

"""
A simple tool for listing and fetching GitHub pull requests
See README.md

"""

import requests
import sys
from subprocess import PIPE, Popen
import os
import platform

"""
Extract GitHub short url from git in current directory
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
List pull requests, returns GitHub JSON
"""
def list_pull_requests(url):
    r = requests.get('https://api.github.com/repos/%s/pulls' % url)
    if r.status_code != 200:
        print("GitHub returned %s" % r.status_code)
        return None
    else:
        return r.json()

"""
Checkout the specified PR (GitHub JSON)
"""
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

"""
Open url in browser
"""
def open_url(url):
    if "Darwin" in platform.platform():
        os.system("open %s" % (url))
    elif "Linux" in platform.platform():
        os.system("xdg-open \"\" %s" % (url))
    elif "Windows" in platform.platform():
        os.system("start \"\" %s" % (url))
    else:
        print("What is this? OS/2 ;)")

"""
Print usage
"""
def usage():
    print("Usage: %s [-l] [-c <id>] [-v <id>]" % sys.argv[0])
    print(" -l       List pull requests in current GitHub repo")
    print(" -c <id>  Checkout PR on a separate branch")
    print(" -v <id>  Open PR in browser")
    sys.exit(0)


# main!
if len(sys.argv) == 1:
    usage()

url = github_url()
if url:
    if sys.argv[1] == "--list" or sys.argv[1] == "-l":
        prs = list_pull_requests(url)
        if len(prs) == 0:
            print("No pull requests")
        else:
            for pr in prs:
                print(" %15s  %3s   %s" % (pr['user']['login'], pr['number'], pr['title']))
#            print("%s" % (pr['body'].strip()))
    elif sys.argv[1] == "--check-out" or sys.argv[1] == "-c":
        try:
            pr_id = int(sys.argv[2])
        except IndexError:
            usage()
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
    elif sys.argv[1] == "--view" or sys.argv[1] == "-v":
        try:
            pr_id = int(sys.argv[2])
        except IndexError:
            usage()
        prs = list_pull_requests(url)
        if len(prs) == 0:
            print("No pull requests")
        else:
            found = False
            for pr in prs:
                if int(pr['number']) == pr_id:
                    found = True
                    open_url(pr["_links"]["html"]["href"].decode('utf-8'))
            if not found:
                print("PR %d not found." % pr_id)
