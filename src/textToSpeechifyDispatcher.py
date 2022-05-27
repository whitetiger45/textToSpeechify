# -*- coding: utf-8 -*-
#!/bin/python
# author: bryan kanu
# description: 
#   this program simply reads an input file containing urls, 
#   uses the command line utility wget to download that resource, 
#   and then dispatches textToSpeechify.py on the downloaded blob.
#   only the text of the blog articles will be written to the output
#   file. 
# note:
#   this is a stable, dirty version of what is a work in progress; 
#   as more files are consumed, it will be improved.
import urllib.request
import os, re, traceback

from pathlib import Path
from subprocess import check_call, check_output

cout_t = {"info":"*","error":"x","success":"✓","debug":"DEBUG","warn":"!"}
python = "python3.8"
cwd = Path(os.getcwd())

def cout(message_type,message):
    print(f"[{cout_t[message_type]}] {message}")

def downloadUrl(url):
    blob = "blob.html"
    cout("info",f"Downloading {url}.")

    try:
        cmd = check_call(["wget", f"-O", f"{blob}", f"{url}"])
    except:
        cout("error",f"{traceback.format_exc()}")
    else:
        dispatchTextToSpeechify(blob)

def dispatchTextToSpeechify(blob):
    cout("info",f"Dispatching textToSpeechify.")
    try:
        textToSpeechify = list(Path(cwd.parent).rglob("textToSpeechify.py"))[0]
        outPath = "output.txt"
        ret = check_output([f"{python}", f"{textToSpeechify}", "-f", f"{blob}", "-O", f"{outPath}"])
        ret = "".join(line for line in ret.decode("utf-8","ignore").split("\n"))
        if re.search("\[x\]",ret):
            cout("error",f"{ret}")
        else:
            cout("success"," ")
    except:
        cout("error",f"{traceback.format_exc()}")

def main(in_file):
    try:

        cout("info",f"Reading {in_file}.")
        with open(in_file,"r") as fd:
            urls = [ url.strip() for url in fd.readlines() ]
        cout("success","# of urls read: {len(urls)}.")

        # filter out pdfs for now until we can build in support for dynamic calls to
        # pdftothml
        pdfs = list(filter((lambda url: Path(url).suffix == ".pdf"), urls))
        if pdfs:
            urls = list(set(urls) - set(pdfs))
            cout("warn",f"textToSpeechify does not currently support dynamic creation of html files from pdfs.")
            cout("warn",f"These files have been filtered from your urlFeed: {pdfs}.")

        if urls:
            for url in urls:
                downloadUrl(url)
        else:
            cout("info",f"Uh-oh...there was a problem. Check to make sure the urls in {in_file} are correct, then try again.")
    except:
        cout("error",f"{traceback.format_exc()}")

if __name__ == '__main__':
    in_file = "urlFeed.txt"
    cout("success","Running.")
    main(in_file)
    cout("success",f"Done.")
