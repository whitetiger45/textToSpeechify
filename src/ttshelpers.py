# -*- coding: utf-8 -*-
#!/bin/python3
# author: bryan kanu
# description: 
#   textToSpeechify module functions and global variables
# note:
#   this is a stable, dirty version of what is a work in progress; 
#   as more files are consumed, it will be improved.
import os, platform, re, traceback
from pathlib import Path
from subprocess import check_call, check_output

# ENUM VARS #
USAGE = -1
SUCCESS = 0
NOT_SERIOUS = 3
FATAL = 6

# LAMBDA FUNCTIONS #
deflate = lambda lst: list(filter((lambda l: l != ""),lst))
# normalize a unicode string and remove escape bytes
normalize = lambda line: line.encode("ascii","ignore").decode("ascii","ignore")

# GLOBAL VARIABLES #
cout_t = {"info":"*","error":"x","success":"✓","debug":"DEBUG","warn":"!"}
cwd = Path(os.getcwd())
name = "textToSpeechify"
python = "python3"
tag_t = {
0:"title",
1:"p",
2:"a",
3:"b",
4:"em",
5:"i",
6:"img",
7:"figure",
8:"strong",
9:"li",
10:"div",
11:"ol",
12:"ul",
13:"span",
14:"polygon",
15:"path",
16:"script",
17:"style"
}
ttsPath = list(cwd.parent.rglob("textToSpeechify.py"))[-1]
# these are tags that we want to avoid copying to our output file.
skip_tag_t = [tag_t[6],tag_t[7],tag_t[14],tag_t[15],tag_t[16],tag_t[17]]
version = "2.1"

# GLOBAL FUNCTIONS #
def cout(message_type,message):
    print(f"[{cout_t[message_type]}] {message}")

def downloadUrl(url):
    blob = "blob.html"
    cout("info",f"Downloading {url}.")

    try:
        cmd = check_call(["curl", "-L", "-o", f"{blob}", f"{url}"],
            encoding="utf-8",errors="ignore")
    except:
        cout("error",f"{traceback.format_exc()}")
    else:
        dispatchTextToSpeechify(blob)

def dispatchTextToSpeechify(blob):
    cout("info",f"Dispatching textToSpeechify.")
    try:
        outPath = "output.txt"
        ret = check_output([f"{python}", f"{ttsPath}", "-f", f"{blob}", "-O", f"{outPath}"],
            encoding="utf-8",errors="ignore")
        if re.search("\[x\]",ret):
            cout("error",f"{ret}")
        else:
            cout("success"," ")
    except:
        cout("error",f"{traceback.format_exc()}")

def flatten(lines):
    return [line for lst in lines for line in lst]

def windows():
    pltfrm = platform.system().lower()
    return pltfrm == "windows"
