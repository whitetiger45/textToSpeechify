# -*- coding: utf-8 -*-
#!/bin/python
# author: bryan kanu
# description: 
#   this program simply loops through the headlines for https://thehackernews.com/, downloads them
#   and writes only the text of the blog articles to a file so they can be read aloud with a 
#   text-to-speech program to facilitate multi-tasking.
# note:
#   this is a stable, dirty version of what is a work in progress; 
#   as more files are consumed, it will be improved.
import urllib.request
import os, re, sys, traceback

from pathlib import Path

src = list(Path(Path(os.getcwd()).parent).rglob("ttshelpers.py"))[-1].parent
sys.path.insert(0, f"{src}")

import ttshelpers as ttsh

sites = {"https://thehackernews.com/":"""<a class=\Sstory-link\S href="(.*)">""",
"https://packetstormsecurity.com/news/":"""<dt><a href="/news/(view/.*)">"""}
grepStories = lambda expr,line: re.finditer(expr,line)

def getYesterdaysNews():
    ret = []
    try:
        if os.path.exists(out_file):
            with open(out_file,"r") as fd:
                ret = [line.strip() for line in fd.readlines()]
    except:
        cout("error",f"{traceback.format_exc()}")
    return ret

def main():
    try:
        latestNews = []
        for site,pattern in sites.items():
            ttsh.downloadUrl(site)
            with open(ttsh.blob,"r") as fd:
                siteLandingPage = [ line.strip() for line in fd.readlines() ]
            latestNews += ttsh.flatten(list(map((lambda line: [m.group(1) if site in m.group(1) else f"{site}{m.group(1)}" for m in grepStories(pattern,line)]),siteLandingPage)))
        yesterdaysHeadlines = getYesterdaysNews()
        latestNews = list(set(latestNews) - set(yesterdaysHeadlines))
        if latestNews:
            with open(out_file, "a") as fd:
                [ fd.write(f"{line}\n") for line in latestNews ]

            for headline in latestNews:
                ttsh.downloadUrl(headline)
                ttsh.dispatchTextToSpeechify()
        else:
            cout("info","You've read all of the latest articles. Check back in a couple hours.")

    except:
        cout("error",f"{traceback.format_exc()}")

if __name__ == '__main__':
    cout = ttsh.cout
    out_file = "latestNews.txt"
    cout("success","Running.")
    main()
    cout("success",f"Done. Today's headlines saved to {out_file}.")
