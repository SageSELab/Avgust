#extract the element and locate it from the dot file.

import re

import os

from collections import defaultdict
import argparse


def find_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if start not in graph:
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath: return newpath
    return None

def findXPath(inputImagePath, dotPath):
    # dotPath="python-android/testAOLVideo/S0/graph.dot"
    # inputImagePath="python-android/testAOLVideo/S0/pngs/30_372_1050_522.png"


    linenum = r"^\t(\d+)\s+\["
    lineregex = re.compile(linenum)
    dotRegex = re.compile(r"^\t(\d+) -> (\d+)")
    matchedList = []
    with open(dotPath) as search:
        for line in search:
            if os.path.basename(inputImagePath) in line:
                match = lineregex.match(line)
                if match:
                    linenum = int(match.group(1))
                    matchedList.append(int(linenum))
    # print("The list is:{}".format(matchedList))
    maxlinenum = max(matchedList)
    # print("The max line number is:{}".format(maxlinenum))

    dic = defaultdict(list)

    with open(dotPath) as search:
        for line in search:
            match = dotRegex.match(line)
            if match:
                parent = str(match.group(1))
                child = str(match.group(2))
                
                dic[parent].append(child)



    contentRegex = re.compile(r"\|(.+) = (.*)")
    path = find_path(dic, str(0), str(maxlinenum))

    # print("The path is:{}".format(path))
    trans = re.compile(r"\[label=\"(.+)\"\]")

    jsonlist = []
    for elem in path:
        with open(dotPath) as search:
            for line in search:
                if re.search(rf"^\t{elem}\s+\[", line):
                    match = trans.search(line)
                    json = {}
                    if match:
                        content = match.group(1).replace('\\l','\n').replace('}','').replace('{','|')
                        # print(content)
                        for sline in content.splitlines():
                            mat = contentRegex.search(sline)
                            if mat:
                                json[mat.group(1)] = mat.group(2)
                        # print(json)
                        jsonlist.append(json)

    xpath = ""
    for elem in jsonlist:
        if "numInParentLayout" in elem:
            # if elem["numInParentLayout"] != "0":
            xpath += "/{}[{}]".format(elem["class"], str(int(elem["numInParentLayout"]) + 1))
            # else:
            #     xpath += "/{}".format(elem["class"])
        else:
            xpath += "/{}".format(elem["class"])
    # print(xpath)
    return xpath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Given an cropped element path, Find element\'s xPath in the layout from existing dot file ")
    parser.add_argument('inputImagePath', action="store")
    parser.add_argument('dotPath', action="store")
    args = parser.parse_args()
    findXPath(args.inputImagePath, args.dotPath)
    pass

