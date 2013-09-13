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

class NodeParser(ast.NodeVisitor):
    source_code = []
    source_code_len = 0
    lines_depth = []
    path = ""
    name = ""

    def __init__(self, code_list, name, path):
        self.source_code = code_list
        self.source_code_len = len(code_list)-1
        self.lines_depth = [65535] * (self.source_code_len+1)
        self.path = path
        self.name = name

    def addAttributes(self, node):
        for node in node.body:
            # process attributes
            # TODO: I dont think my solution is proper
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        attr = Attribute.addAttribute(name=target.attr, module_id=node.module_id, class_id=node.class_id)
                        attr.code = source_code[node.lineno]
                        attr.save()
                    elif isinstance(target, ast.Name):
                        attr = Attribute.addAttribute(name=target.id, module_id=node.module_id, class_id=node.class_id)
                        attr.code = source_code[node.lineno]
                        attr.save()
                    else:
                        # I do not know how to handle these cases
                        pass

    def generic_visit(self, node, module_id=None, class_id=None, function_id=None):
        self.markLineDepth(node)
        depth = node.depth
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if self.continue_or_not(item, depth):
                        item.depth = depth+1
                        self.lines_depth[item.lineno] = item.depth
                        item.module_id = node.module_id
                        item.class_id = node.class_id
                        item.function_id = node.function_id
                        self.visit(item)
            elif self.continue_or_not(value, depth):
                value.depth = depth+1
                self.lines_depth[value.lineno] = value.depth
                value.module_id = node.module_id
                value.class_id = node.class_id
                value.function_id = node.function_id
                self.visit(value)

    def continue_or_not(self, x, depth):
        if not isinstance(x, ast.AST):
            return False
        if not hasattr(x, "lineno"):
            return False
        existing_depth = self.lines_depth[x.lineno]
        if existing_depth != 65535 and depth+1 < existing_depth:
            return False
        return True

    def visit_Module(self, node):
        module = Module.addModule(name=self.name, path=self.path)
        node.module_id = module.id
        if self.source_code_len > 0:
            code = self.getSourceCode(1, self.source_code_len)
        else:
            code = ""
        module.code = code
        module.lines = self.source_code_len
        module.save()
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.lines_depth[node.lineno] = node.depth
        cls = Class.addClass(name=node.name, module_id=node.module_id, class_id=node.class_id)
        node.class_id = cls.id
        self.generic_visit(node)
        lastLine = self.getLastLine(node.lineno, node.depth)
        code = self.getSourceCode(node.lineno, lastLine)
        cls.code = code
        cls.save()
        self.addAttributes(node)

    def visit_FunctionDef(self, node):
        self.lines_depth[node.lineno] = node.depth
        fun = Function.addFunction(name=node.name, module_id=node.module_id, class_id=node.class_id, function_id=node.function_id)
        node.function_id = fun.id
        self.generic_visit(node)
        lastLine = self.getLastLine(node.lineno, node.depth)
        code = self.getSourceCode(node.lineno, lastLine)
        fun.code = code
        fun.save()

    def getSourceCode(self, start_line, end_line):
        code = self.source_code[start_line: end_line+1]
        # remove the blank lines at the end of section
        while not code[-1].strip(" \r\n\t"):
            code.pop()
        return "".join(code)

    def getLastLine(self, line_num, depth):
        for idx in xrange(line_num+1, self.source_code_len+1):
            if self.lines_depth[idx] > depth:
                line_num = idx
            else:
                break
        return line_num

    def markLineDepth(self, item):
        if hasattr(item, "lineno"):
            self.lines_depth[item.lineno] = item.depth
        if hasattr(item, "body"):
            if not isinstance(item.body, list):
                self.lines_depth[item.body.lineno] = item.depth+1
            else:
                for node in item.body:
                    self.lines_depth[node.lineno] = item.depth+1

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
                try:
                    with open(fullpath, "r") as f1:
                        print fullpath
                        source_code.append("")
                        for line in f1:
                            try:
                                source_code.append(line.decode('utf-8'))
                            except UnicodeDecodeError:
                                source_code.append(line.decode('iso-8859-1'))

                    with open(fullpath, "rb") as f2:
                        tree = ast.parse(f2.read())
                        tree.depth = 0
                        x = NodeParser(source_code, name=f[:-name_offset], path=root[path_offset:])
                        tree.module_id = None
                        tree.class_id = None
                        tree.function_id = None
                        x.visit(tree)
                        # print x.lines_depth
                    #with open(fullpath, "rb") as f:
                    #    parseModule(f.read(), module_id=module_id, depth=0)
                except Exception:
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
