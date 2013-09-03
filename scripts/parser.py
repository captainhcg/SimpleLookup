import sys
sys.path.append('../')
import settings
import traceback

import ast
import os, os.path
import parser_helper

verbose = False
source_code = []

def parseNode(item, module_id=0, class_id=0, function_id=0):
    call = parseOther
    if isinstance(item, ast.FunctionDef):
        call = parseFunction
    elif isinstance(item, ast.ClassDef):
        call = parseClass
    return call(item, module_id, class_id, function_id)

def parseOther(item, module_id=0, class_id=0, function_id=0):
    lastLine = item.lineno
    if hasattr(item, "body"):
        if not isinstance(item.body, list):
            item.body = [item.body]
        for node in item.body:
            lastLine = parseNode(node, module_id, class_id, function_id)
    return lastLine

def parseFunction(item, module_id=0, class_id=0, function_id=0):
    global source_code, verbose
    function_id = parser_helper.addFunction(item.name, module_id, class_id, function_id)
    start_line = item.lineno
    end_line = item.lineno
    for node in item.body:
        end_line = parseNode(node, module_id, class_id, function_id)

    if verbose:
        print "function: %s"%item.name
    code = u"".join(source_code[start_line: end_line+1])
    parser_helper.setFunctionCode(function_id, code)
    return end_line

def parseClass(item, module_id=0, class_id=0, function_id=0):
    global source_code, verbose
    class_id = parser_helper.addClass(item.name, module_id, class_id)
    start_line = item.lineno
    end_line = item.lineno
    for node in item.body:
        end_line = parseNode(node, module_id, class_id, function_id)
        # process attributes
        # TODO: I dont think my solution is proper
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    parser_helper.addAttribute(target.attr, module_id, class_id, source_code[node.lineno])
                elif isinstance(target, ast.Name):
                    parser_helper.addAttribute(target.id, module_id, class_id, source_code[node.lineno])
                else:
                    # I do not know how to handle these cases
                    if verbose:
                        print type(target), source_code[node.lineno]
    if verbose:
        print "class: %s"%item.name
    code = "".join(source_code[start_line: end_line+1])
    parser_helper.setClassCode(class_id, code)
    return end_line

def parseModule(source, module_id=0):
    tree = ast.parse(source)
    if not hasattr(tree, "body"):
        return
    for item in tree.body:
        parseNode(item, module_id)

def main(argv=sys.argv):
    global source_code
    if len(argv)<2:
        project_id = 0
    else:
        try:
            project_id = int(argv[1])
        except:
            project_id = 0
    PROJECT_PATH = settings.PROJECTS[project_id]["PROJECT_PATH"]
    parser_helper.reset(project_id=project_id)
    for root, dirs, files in os.walk(PROJECT_PATH):
        name_offset = len(settings.FILE_EXTENSION)
        path_offset = len(PROJECT_PATH)
        for f in files:
            if f.endswith(settings.FILE_EXTENSION):
                fullpath = os.path.join(root, f)
                source_code = []
                module_id = parser_helper.addModule(f[:-name_offset], root[path_offset:])
                try:
                    with open(fullpath, "rb") as f:
                        source_code.append("")
                        for line in f:
                           source_code.append(line.decode('utf-8')) 
                    with open(fullpath, "rb") as f:
                        parseModule(f.read(), module_id=module_id)
                except Exception as e:
                    traceback.print_exc()
                    exit()

if __name__ == "__main__":
    main()
