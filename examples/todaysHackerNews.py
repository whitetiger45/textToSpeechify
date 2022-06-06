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
from subprocess import check_call, check_output

sites = {"https://thehackernews.com/":"""<a class=\Sstory-link\S href="(.*)">""",
"https://packetstormsecurity.com/news/":"""<dt><a href="/news/(view/.*)">"""}
grepStories = lambda expr,line: re.finditer(expr,line)
cout_t = {"info":"*","error":"x","success":"✓","debug":"DEBUG","warn":"!"}
python = "python3.8"
cwd = Path(os.getcwd())

def cout(message_type,message):
    print(f"[{cout_t[message_type]}] {message}")

def flatten(lines):
    return [line for lst in lines for line in lst]

def downloadUrl(url):
    blob = "blob.html"
    cout("info",f"Downloading {url}.")

    try:
        cmd = check_call(["curl", "-L", "-o", f"{blob}", f"{url}"])
    except:
        cout("error",f"{traceback.format_exc()}")
    else:
        dispatchTextToSpeechify(blob)

def dispatchTextToSpeechify(blob):
    try:
        textToSpeechify = list(Path(cwd.parent).rglob("textToSpeechify.py"))[0]
        outPath = Path(cwd).joinpath("output.txt")
        ret = check_output([f"{python}", f"{textToSpeechify}", "-f", f"{blob}", "-O",f"{outPath}"])
        ret = ret.decode("utf-8","ignore")
        if re.search("\[x\]",ret):
            cout("warn",f"{ret}")
    except:
        cout("error",f"{traceback.format_exc()}")

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
            with urllib.request.urlopen(site) as fd:
                siteLandingPage = [ line.decode("utf-8").strip() for line in fd.readlines() ]
            latestNews += flatten(list(map((lambda line: [m.group(1) if site in m.group(1) else f"{site}{m.group(1)}" for m in grepStories(pattern,line)]),siteLandingPage)))
        yesterdaysHeadlines = getYesterdaysNews()
        latestNews = list(set(latestNews) - set(yesterdaysHeadlines))
        # cout("debug",f"# of new articles: {len(latestNews)}")
        # cout("debug",f"new articles: {latestNews}")
        if latestNews:
            with open(out_file, "a") as fd:
                [ fd.write(f"{line}\n") for line in latestNews ]

            for headline in latestNews:
                downloadUrl(headline)
        else:
            cout("info","You've read all of the latest articles. Check back in a couple hours.")

    except:
        cout("error",f"{traceback.format_exc()}")

if __name__ == '__main__':
    out_file = "latestNews.txt"
    cout("success","Running.")
    main()
    cout("success",f"Done. Today's headlines saved to {out_file}.")
