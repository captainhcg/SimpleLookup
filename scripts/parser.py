import sys
sys.path.append('../')
import settings
import traceback

import inspect
import ast
import os, os.path

print settings.PROJECT_PATH

verbose = False
sys.path.append(settings.PROJECT_PATH)
source_code = []

def parseOther(item):
    lastLine = item.lineno
    if hasattr(item, "body"):
        if not isinstance(item.body, list):
            item.body = [item.body]
        for node in item.body:
            lastLine = parseNode(node)
    return lastLine

def parseNode(item):
    if isinstance(item, ast.FunctionDef):
        return parseFunction(item)
    elif isinstance(item, ast.ClassDef):
        return parseClass(item)
    else:
        return parseOther(item)

def parseFunction(item):
    start_line = item.lineno
    end_line = item.lineno
    for node in item.body:
        end_line = parseNode(node)

    if verbose:
        print "function: %s"%item.name
        print start_line, end_line
    code = "".join(source_code[start_line: end_line+1])
    return end_line

def parseClass(item):
    start_line = item.lineno
    end_line = item.lineno
    for node in item.body:
        end_line = parseNode(node)

    if verbose:
        print "class: %s"%item.name
        print start_line, end_line
    code = "".join(source_code[start_line: end_line+1])
    print "st:%d"%start_line, code, end_line
    return end_line

def parseModule(source):
    tree = ast.parse(source)
    if not hasattr(tree, "body"):
        return
    for item in tree.body:
        if isinstance(item, ast.FunctionDef):
            parseFunction(item)
        elif isinstance(item, ast.ClassDef):  
            parseClass(item)

for root, dirs, files in os.walk(settings.PROJECT_PATH):
    for f in files:
        if f.endswith(settings.FILE_EXTENSION):
            fullpath = os.path.join(root, f)
            source_code = []
            print fullpath
            try:
                # (name, suffix, mode, mtype) = inspect.getmoduleinfo(fullpath)
                # print (name, suffix, mode, mtype)
                with open(fullpath, "rb") as f:
                    source_code.append("")
                    for line in f:
                       source_code.append(line) 
                with open(fullpath, "rb") as f:
                    parseModule(f.read())
            except Exception as e:
                traceback.print_exc()
                exit()
            # print fullpath