# -*- coding: utf-8 -*-
#!/bin/python3
# author: bryan kanu
# description: 
#   this is a program to strip html tags. I use it to get the text 
#   from blog articles so I can listen (currently using https://ttsreader.com/) to them and multi-task.
# note:
#   this is a stable, dirty version of what is a work in progress; 
#   as more files are consumed, it will be improved.
import argparse, copy, html
import os, re, string, sys, traceback
import ttshelpers as ttsh

from collections import deque
from pathlib import Path

# a function for looking up the index of HTML element tag indexes in tag_t
index = lambda v: list(tag_t.values()).index(v)

# regular expressions to find html tags
# i.e. <h4 style="text-align: left;"><strong>3 </strong>&#8212; <strong>Collection</strong></h4><ol>
addNewline = lambda line: line.replace("><",">\n<")
findTagsInline = lambda line: re.finditer("><",line)
findTags = lambda line: re.finditer("<([\S]+).*?>(.*?)</.*?>|<([0-9a-zA-Z]+).*?>(.*?)",line)
stripTagL = lambda line: re.match("</*([0-9a-zA-Z]+).*?>(.+)",line)
stripPDFToHTMLTagL = lambda line: re.match("</*[0-9a-zA-Z]+.*?>(.+)",line)
stripReference = lambda line: re.match("\[[0-9]+\]", line)
# list(map((lambda l: [m.groups() for m in findTags(l)]),lines)) # helper for debugging

# strip html encoding
def stripEncoding(line):
    tmp = re.search("&\S+;",line)
    if tmp:
        x = tmp.span()[0]; y = line.find(";")
        if y > x:
            tmpLine = line[0:x] + line[y+1:]
        #cout("info",f"[stripEncoding] tmp.span(): {tmp.span()} | tmpLine: {tmpLine}")
        return stripEncoding(tmpLine)
    return line

def getBlankElementsInRange(blanks, start, end):
    tmp = []
    for idx,e in enumerate(blanks):
        if idx <= start or idx >= end:
            tmp.append(e)
    return tmp

# a function for looking up the index of HTML element tag indexes in tag_t
def lookupKey(dct,value):
    for k,v in dct.items():
        if value == v:
            return k

# function to calculate the distance of the largest number 
# of consecutive empty strings in the state object
DISTANCE_TRESHOLD = 0x8
def getDistance(blanks):
    # cout("info",f"blanks: {blanks}")
    distanceObj = {"s_idx":-1,"e_idx":-1,"value":0,"maxDistance":0}
    startIdx = blanks[0]; tmpDict = {startIdx:0};
    for idx in range(1,len(blanks)):
        tmp = blanks[idx] - blanks[idx-1]
        if tmp == 1:
            tmpDict[startIdx] += 1           
        else:
            startIdx = blanks[idx]
            tmpDict.update({startIdx:0})
            distanceObj["s_idx"] = idx-1

    # cout("debug",f"distances: {tmpDict}")
    maxDistance = max(tmpDict.values())
    distanceObj["maxDistance"] = maxDistance
    distanceObj["s_idx"] = blanks.index(lookupKey(tmpDict,maxDistance))
    distanceObj["e_idx"] = distanceObj["s_idx"] + maxDistance
    # cout("debug",f"maxDistance: {maxDistance}")
    # cout("debug",f"s_idx: {distanceObj['s_idx']}")
    # cout("debug",f"e_idx: {distanceObj['e_idx']}")
    # cout("debug",
        # f"largest gap in blanks starts at {distanceObj['s_idx']} until {distanceObj['e_idx']}")
    return distanceObj

def getStatesIndexes(state):
    blanks = []
    x = -1; y = -1;
    for idx in range(0,len(state)):
        if state[idx] != "":
            x = idx
            break
    for idx in range(len(state)-1,0,-1):
        if state[idx] != "":
            y = idx
            break
    for idx in range(x,y):
        if state[idx] == "":            
            # cout("debug",f"{idx}) {state[idx]}")
            # if state[idx+1] != "":
                # cout("debug",f"{idx+1}) {state[idx+1]}")
            blanks.append(idx)

    distanceObj = getDistance(blanks)
    blanks = getBlankElementsInRange(blanks,distanceObj["s_idx"],distanceObj["e_idx"])
    blanks.sort()
    #cout("debug",f"(x={x},y={y})")
    # cout("debug",f"state[{x}]: {state[x]}")
    # cout("debug",f"state[{y}]: {state[y]}")
    # cout("debug",f"blanks: {blanks}")
    cout("debug",f"distanceObj: {distanceObj}")
    return x,y,blanks,distanceObj["s_idx"],distanceObj["e_idx"]

def replace(**kwargs):
    idx = kwargs["idx"]
    kwargs["state"][idx] = kwargs["value"]

def parseHTMLFile(lines):
    global STATUS
    documentText = []
    try:
        stepOne = "".join(line for line in lines)
        stepTwo = stepOne.replace("<","\n<")
        stepThree = stepTwo.find("</head>\n")
        stepFour = stepTwo[stepThree+len("</head>\n"):]
        stepFiveA = re.search("<p[\s]*.*?>",stepFour,flags=re.IGNORECASE)
        stepFiveB = re.search(">p/<",stepFour[-1:0:-1],flags=re.IGNORECASE)
        if stepFiveA and stepFiveB:
            stepFiveA = stepFiveA.span()[0]
            # stepFiveB = stepFour[-1:0:-1].find(">p/<")
            stepFiveB = stepFiveB.span()[0]
            stepFiveB = len(stepFour)-(stepFiveB+len(">p/<"))
            stepSix = stepFour[stepFiveA:stepFiveB].split("\n")
            for line in stepSix:
                m = stripTagL(line)
                if m and m[1] not in ttsh.skip_tag_t:
                    documentText.append(m[2])
            # cout("debug",f"{documentText}")
        else:
            cout("error","Did not find one, either, or both of the initial '<p>' and closing </p> tags. Time for an upgrade!")
    except:
        cout("error",f"{traceback.format_exc()}")
    return documentText

# this function is used to create speech-to-text-ready text from html files generated using the unix utility pdftohtml
def parsePDFToHTMLFile(lines):
    global STATUS
    documentText = []
    try:
        stepOne = "".join(line for line in lines)
        stepOne = stepOne.replace("<","\n<")
        stepTwo = stepOne.find("</head>\n")
        stepTwo = stepOne[stepTwo+len("</head>\n"):]
        stepThreeA = re.search("<body[\s]*.*?>",stepTwo,flags=re.IGNORECASE)
        # stepThreeB = stepTwo[-1:0:-1].find(">ydob/<")
        stepThreeB = re.search(">ydob/<",stepTwo[-1:0:-1],flags=re.IGNORECASE)
        if stepThreeA and stepThreeB:
            stepThreeA = stepThreeA.span()[0]
            stepThreeB = stepThreeB.span()[0]
            stepThreeB = len(stepTwo)-(stepThreeB+len(">ydob/<"))
            stepTwo = stepTwo[stepThreeA:stepThreeB].split("\n")
            for line in stepTwo:
                m = stripPDFToHTMLTagL(line)
                if m:
                    documentText.append(m[1])
        else:
            cout("error",f"Did not find one of the 'body' tags. Locations (<body>,</body>): ({stepThreeA},{stepThreeB}). Time for an upgrade!")
    except:
        cout("error",f"{traceback.format_exc()}")
    return documentText

def saveParsedFile(state):
    global STATUS
    try:
        with open(out_file, "a") as fd:
            for idx in range(0,len(state)-1):
                if(
                    state[idx][-1] == " " or
                    state[idx+1][0] == " " or
                    state[idx+1][0] in string.punctuation
                ):
                    if state[idx][-1] == " " or state[idx+1][0] == " ":
                        fd.write(f"{state[idx]}")
                    else:
                        fd.write(f"{state[idx]} ")
                else:
                    fd.write(f"{state[idx]}\n")
            fd.write(f"{state[-1]}\n")
            fd.write("\n")
    except:
        cout("error",f"{traceback.format_exc()}")
        STATUS = ttsh.NOT_SERIOUS

def main(argv):
    global STATUS
    in_file = argv.in_file
    lines = []
    try:
        with open(in_file, "r", encoding="utf-8", errors="ignore") as fd:
            lines = [ line.strip() for line in fd.readlines() ]
        state = []
        if argv.htmlfrompdf:
            state = parsePDFToHTMLFile(lines)
        else:    
            state = parseHTMLFile(lines)
        state = list(map(html.unescape,state))
        state = list(map(ttsh.normalize,state))
        state = ttsh.deflate(state)
        
        ###########################################################################################
        # 2022.05.26
        # note: 
        #   more work needed because of exception thrown when using normalize for unicode strings
        # htmlBodyStart,htmlBodyEnd,emptyLinesIdxList,emptyLinesListStartIdx,emptyLinesListEndIdx = getStatesIndexes(state)
        # cout("debug",f"{state}")
        ###########################################################################################
        if state:
            saveParsedFile(state)
        else:
            cout("warn","Uh-oh...state is empty. Check program output(s) to see what went wrong.")
            STATUS = ttsh.NOT_SERIOUS
    except:
        cout("error",f"{traceback.format_exc()}")
        STATUS = ttsh.FATAL

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog=f"{ttsh.name}", description="Prepare text for speech.")
    parser.add_argument("--version", action="version", version=f"{ttsh.name} {ttsh.version}")
    parser.add_argument("-f", "--file", dest="in_file", metavar="HTML_FILE", type=Path, required=True,
        help="html file to be parsed")    
    parser.add_argument("-hfp","--htmlfrompdf", dest="htmlfrompdf", 
        action="store_true", 
        help="html file generated from a pdf file using pdftohtml")
    parser.add_argument("-O", "--output", dest="out_file", type=Path, default="output.txt",
        help="file to write output to")

    cout = ttsh.cout
    argv = parser.parse_args()
    # cout("debug",f"{argv}")
    STATUS = ttsh.SUCCESS
    out_file = argv.out_file
    cout("success","Running.")
    main(argv)
    if STATUS == ttsh.SUCCESS:
        cout("success",f"Done. Check {out_file}.")
    else:
        cout("error",f"return code: {STATUS}")
