import sys
import settings
import traceback
import re
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
    project_settings = settings.PROJECTS[project_id]
    project_path = project_settings["PROJECT_PATH"]
    parser_helper.reset(project_id=project_id)
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
                print fullpath
                source_code = []
                module_id = parser_helper.addModule(f[:-name_offset], root[path_offset:])
                try:
                    with open(fullpath, "rb") as f:
                        source_code.append("")
                        for line in f:
                            try:
                                source_code.append(line.decode('utf-8'))
                            except UnicodeDecodeError:
                                source_code.append(line.decode('iso-8859-1'))
                    with open(fullpath, "rb") as f:
                        parseModule(f.read(), module_id=module_id)
                except Exception as e:
                    traceback.print_exc()
                    exit()
    parser_helper.closeConn()

if __name__ == "__main__":
    main()
