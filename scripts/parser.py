#!/usr/bin/env python
import sys
sys.path.append("../")

import settings
import traceback
import re
import ast
import os, os.path
from search_app.models import Module, Class, Function, Attribute
from search_app.models import setProject, resetDB
from optparse import OptionParser

source_code = []
lines_depth = []
source_code_len = 0

def parseNode(item, module_id=None, class_id=None, function_id=None, depth=0):
    call = parseOther
    if isinstance(item, ast.FunctionDef):
        call = parseFunction
    elif isinstance(item, ast.ClassDef):
        call = parseClass
    return call(item, module_id, class_id, function_id, depth+1)

def markLineDepth(item, depth):
    global lines_depth
    if hasattr(item, "lineno"):
        lines_depth[item.lineno] = depth
    if hasattr(item, "body"):
        if not isinstance(item.body, list):
            item.body = [item.body]
        for node in item.body:
            lines_depth[node.lineno] = depth+1

def getLastLine(line_num, depth):
    global source_code_len
    for idx in xrange(line_num+1, source_code_len+1):
        if lines_depth[idx] > depth:
            line_num = idx
        else:
            break
    return line_num

def getSourceCode(start_line, end_line):
    global source_code
    code = source_code[start_line: end_line+1]
    # remove the blank lines at the end of section
    while not code[-1].strip(" \r\n"):
        code.pop()
    return "".join(code)

def parseOther(item, module_id=None, class_id=None, function_id=None, depth=0):
    lastLine = item.lineno
    markLineDepth(item, depth)
    if hasattr(item, "body"):
        if not isinstance(item.body, list):
            item.body = [item.body]
        for node in item.body:
            lastLine = parseNode(node, module_id, class_id, function_id, depth+1)
    return lastLine

def parseFunction(item, module_id=None, class_id=None, function_id=None, depth=0):
    fun = Function.addFunction(name=item.name, module_id=module_id, class_id=class_id, function_id=function_id)
    function_id = fun.id
    start_line = end_line = item.lineno
    markLineDepth(item, depth)
    for node in item.body:
        end_line = parseNode(node, module_id, class_id, function_id, depth+1)
    end_line = getLastLine(end_line, depth)
    code = getSourceCode(start_line, end_line)
    fun.code = code
    fun.save()
    return end_line

def parseClass(item, module_id=None, class_id=None, function_id=None, depth=0):
    global source_code
    cls = Class.addClass(name=item.name, module_id=module_id, class_id=class_id)
    class_id = cls.id
    start_line = end_line = item.lineno
    markLineDepth(item, depth)
    for node in item.body:
        end_line = parseNode(node, module_id, class_id, function_id, depth+1)
        # process attributes
        # TODO: I dont think my solution is proper
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    attr = Attribute.addAttribute(name=target.attr, module_id=module_id, class_id=class_id)
                    attr.code = source_code[node.lineno]
                    attr.save()
                elif isinstance(target, ast.Name):
                    attr = Attribute.addAttribute(name=target.id, module_id=module_id, class_id=class_id)
                    attr.code = source_code[node.lineno]
                    attr.save()
                else:
                    # I do not know how to handle these cases
                    # print type(target), source_code[node.lineno]
                    pass
    end_line = getLastLine(end_line, depth)
    code = getSourceCode(start_line, end_line)
    cls.code = code
    cls.save()
    return end_line

def parseModule(source, module_id=None, depth=0):
    tree = ast.parse(source)
    if not hasattr(tree, "body"):
        return
    markLineDepth(tree, depth)
    for item in tree.body:
        parseNode(item, module_id=module_id, depth=depth+1)

def parseProject(project_id=0):
    global source_code, lines_depth, source_code_len
    setProject(project_id)
    resetDB();

    project_settings = settings.PROJECTS[project_id]
    project_path = project_settings['PROJECT_PATH']
    print "Parsing Project %s"%(project_settings['NAME'])
    folder_exclude_patterns = []
    if "FOLDER_EXCLUDE_PATTERNS" in project_settings:
        for pattern in project_settings['FOLDER_EXCLUDE_PATTERNS']:
            folder_exclude_patterns.append(re.compile(pattern))
    for root, dirs, files in os.walk(project_path):
        continue_flag = False
        if folder_exclude_patterns:
            for pattern in folder_exclude_patterns:
                if pattern.search(root):
                    continue_flag = True
                    break
        if continue_flag:
            continue
        name_offset = len(settings.FILE_EXTENSION)
        path_offset = len(project_path)
        for f in files:
            if f.endswith(settings.FILE_EXTENSION):
                fullpath = os.path.join(root, f)
                source_code = []
                lines_depth = []
                module = Module.addModule(name=f[:-name_offset], path=root[path_offset:])
                module_id = module.id
                try:
                    with open(fullpath, "rb") as f:
                        print fullpath
                        source_code.append("")
                        lines_depth.append(65535)
                        for line in f:
                            lines_depth.append(65535)
                            try:
                                source_code.append(line.decode('utf-8'))
                            except UnicodeDecodeError:
                                source_code.append(line.decode('iso-8859-1'))
                    source_code_len = len(source_code)-1
                    if source_code_len > 0:
                        code = getSourceCode(1, source_code_len)
                    else:
                        code = ""
                    module.code = code
                    module.lines = source_code_len
                    module.save()

                    with open(fullpath, "rb") as f:
                        parseModule(f.read(), module_id=module_id, depth=0)
                except Exception as e:
                    traceback.print_exc()
                    exit()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-a", "--all", action="store_true", default=False)
    parser.add_option("-p", "--project", default=0, type="int")
    options, _ = parser.parse_args()

    if options.all:
        for idx in xrange(len(settings.PROJECTS)):
            parseProject(idx)
    else:
        parseProject(options.project)