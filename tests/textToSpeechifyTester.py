# -*- coding: utf-8 -*-
#!/bin/python3
# author: bryan kanu
# description: 
#   this is a program for regression testing textToSpeechify.py. 
# note:
#   this is a stable, dirty version of what is a work in progress; 
#   as more files are consumed, it will be improved.
from pathlib import Path
from subprocess import check_call, check_output

import os, platform, re, sys, traceback

def windows():
    pltfrm = platform.system().lower()
    return pltfrm == "windows"

src = None
if platform.system().lower() == "windows":
    src = list(Path(Path(os.getcwd()).parent).rglob("ttshelpers.py"))[-1].parent
else:
    src = f"{'/'.join(part for part in sys.path[0].split('/')[0:-1])}/src"

sys.path.insert(0,src)
try:
    import ttshelpers as ttsh
except:
    print(f"[x] {traceback.format_exc()}")
    sys.exit()

FAILED_DOWNLOADS = []
FAILED_DISPATCHES = []
FAILED_CONVERSIONS = []
SUCCESSFUL_DISPATCHES = 0

def downloadUrl(url,header=None,outputFile="blob.tests.html"):
    global FAILED_DISPATCHES, SUCCESSFUL_DISPATCHES
    try:
        cout("info",f"Downloading {url}.")
        try:
            if header:
                cmd = check_call(["curl", "-H",f"@{header}" ,"-L", "-o", f"{outputFile}", f"{url}"],
                encoding="utf-8",errors="ignore")
            else:
                cmd = check_call(["curl", "-L", "-o", f"{outputFile}", f"{url}"],
                encoding="utf-8",errors="ignore")
        except:
            FAILED_DOWNLOADS.append(url)
    except:
        cout("error",f"{traceback.format_exc()}")
        FAILED_DISPATCHES.append(url)

def convertPDFToHTML(url,inputFile="blob.tests.pdf2.pdf"):
    if url in FAILED_DOWNLOADS:
        return
    cout("info",f"Converting pdf to html")
    try:
        if ttsh.macOS():
            cmd = check_call(["pdftohtml", "-i", "-q", f"{inputFile}"],
                encoding="utf-8",errors="ignore")
        else:
            cmd = check_call(["pdftohtml", "-i", "-s", "-q", f"{inputFile}"],
                encoding="utf-8",errors="ignore")
    except:
        cout("error",f"{traceback.format_exc()}")
        FAILED_CONVERSIONS.append(url)

def dispatchTextToSpeechify(url,inputFile="blob.tests.html",pdf=False,outputFile="output.txt"):
    global SUCCESSFUL_DISPATCHES
    if url in FAILED_DOWNLOADS or url in FAILED_CONVERSIONS:
        return
    cout("info",f"Dispatching textToSpeechify.")
    try:
        if not pdf:
            ret = check_output([f"{ttsh.python}", f"{ttsh.ttsPath}", "-f", 
                f"{inputFile}", "-O", f"{outputFile}"], encoding="utf-8",errors="ignore")
        else:
            ret = check_output([f"{ttsh.python}", f"{ttsh.ttsPath}", "-f",
                f"{inputFile}", "-O", f"{outputFile}", "-hfp"],
                encoding="utf-8",errors="ignore")
        if re.search("\[x\]",ret):
            FAILED_DISPATCHES.append(url)
            cout("debug",f"{ret}")
        else:
            SUCCESSFUL_DISPATCHES += 1
    except:
        cout("error",f"{traceback.format_exc()}")
        FAILED_DISPATCHES.append(url)

def getTestResults(urls):
    try:
        cout("info","Results:")
        cout("info",f"# of Urls Tested: {len(urls)}")
        cout("info",f"# of Passes: {SUCCESSFUL_DISPATCHES}")
        cout("info",f"# of Failures: {len(FAILED_DISPATCHES)}")
        if len(FAILED_DISPATCHES) != 0:
            cout("info",f"Urls that failed to dispatch: {FAILED_DISPATCHES}")
        if len(FAILED_DOWNLOADS) != 0:
            cout("info",f"# of Failed Downloads: {len(FAILED_DOWNLOADS)}")
            cout("info",f"Urls that failed to download: {FAILED_DOWNLOADS}")
    except:
        cout("error",f"{traceback.format_exc()}")

def main(in_file):
    try:
        cout("info",f"Reading {in_file}.")
        with open(in_file,"r") as fd:
            urls = [ url.strip() for url in fd.readlines() ]
        
        pdfs = list(filter((lambda url: Path(url).suffix.lower() == ".pdf"), urls))
        if pdfs:
            urls = list(set(urls) - set(pdfs))
            if not ttsh.windows():
                if ttsh.checkForPDFToHTML():
                    p = "blob.tests.pdf2"
                    for url in pdfs:
                        downloadUrl(url,outputFile=p+".pdf")
                        convertPDFToHTML(url)
                        if ttsh.macOS():
                            dispatchTextToSpeechify(url,inputFile=p+"s.html",pdf=True)
                            try:
                                ttsh.unlink(p+"_ind.html")
                            except:
                                cout("warn",f"{traceback.format_exc()}")
                        else:
                            dispatchTextToSpeechify(url,inputFile=p+"-html.html",pdf=True)
                    try:
                        ttsh.unlink(p+"-html.html")
                        ttsh.unlink(p+".pdf")
                    except:
                        cout("warn",f"{traceback.format_exc()}")
                else:
                    cout("warn",f"Could not locate pdftotext on your system")
                    cout("warn",f"These files have been filtered from your urlFeed: {pdfs}")
            else:
                cout("warn",f"textToSpeechify does not currently support dynamic creation of text from pdfs on Windows")
                cout("warn",f"These files have been filtered from your urlFeed: {pdfs}")
        if urls:
            for url in urls:
                downloadUrl(url)
                dispatchTextToSpeechify(url)
            getTestResults(urls+pdfs)
        elif not pdfs:
            cout("info",f"Uh-oh...there was a problem. Check to make sure the urls in {in_file} are correct, then try again.")
    except:
        cout("error",f"{traceback.format_exc()}")

if __name__ == '__main__':
    cout = ttsh.cout
    in_file = "urlFeed.TESTS.txt"
    cout("info","Running.")
    main(in_file)
