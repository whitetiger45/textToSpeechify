# -*- coding: utf-8 -*-
#!/bin/python3
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
import ttshelpers as ttsh

from pathlib import Path

def main(in_file):
    try:
        cout("info",f"Reading {in_file}.")
        with open(in_file,"r") as fd:
            urls = [ url.strip() for url in fd.readlines() ]
        cout("success",f"# of urls read: {len(urls)}.")

        # filter out pdfs for now until we can build in support for dynamic calls to
        # pdftothml
        pdfs = list(filter((lambda url: Path(url).suffix == ".pdf"), urls))
        if pdfs:
            urls = list(set(urls) - set(pdfs))
            cout("warn",f"textToSpeechify does not currently support dynamic creation of html files from pdfs.")
            cout("warn",f"These files have been filtered from your urlFeed: {pdfs}.")

        if urls:
            for url in urls:
                ttsh.downloadUrl(url)
        else:
            cout("info",f"Uh-oh...there was a problem. Check to make sure the urls in {in_file} are correct, then try again.")
    except:
        cout("error",f"{traceback.format_exc()}")

if __name__ == '__main__':
    cout = ttsh.cout
    in_file = "urlFeed.txt"
    cout("success","Running.")
    main(in_file)
    cout("success",f"Done.")