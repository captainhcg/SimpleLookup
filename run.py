from flask import Flask, render_template, request, jsonify, g
from flask.ext.sqlalchemy import SQLAlchemy
import Levenshtein
import settings
from functools import wraps
import sqlite3
import sys, os
from models import Module, Class, Function, Attribute, session
from models import setProject
from sqlalchemy.orm import joinedload

app = Flask(__name__)
projects=settings.PROJECTS

# alway pass project_id to view
def init_global(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        global app
        try:
            g.project_id = int(request.args.get('project_id', 0))
        except:
            g.project_id = 0
        setProject(g.project_id)
        db_name = settings.PROJECTS[g.project_id]["DB_NAME"]
        return function(*args, **kwargs)
    return wrap

@app.route('/')
def index():
    return render_template('index.html', projects=projects)

@app.route('/search')
@init_global
def search():
    record_type = request.args.get("type", "")
    if record_type == "class":
        return searchClass(request.args)
    elif record_type == "module":
        return searchModule(request.args)
    elif record_type in ("function", "method"):
        return searchFunction(request.args)

def searchFunction(query):
    record_id = query.get('id')
    fun = session.query(Function).get(record_id)
    data = fun.as_dict()
    return jsonify({"result": data})

def searchClass(query):
    record_id = query.get('id')
    cls = session.query(Class).get(record_id)
    data = cls.as_dict()
    attrs = []
    for attr in cls.attributes:
        attrs.append(attr.as_dict())
    methods = []
    for method in cls.methods:
        methods.append(method.as_dict())
    return jsonify({"result": data, "attrs": attrs, "methods": methods})

def searchModule(query):
    record_id = query.get('id')
    module = session.query(Module).get(record_id)
    data = module.as_dict()
    classes = []
    for cls in module.classes:
        classes.append(cls.as_dict())

    functions = []
    for fun in session.query(Function).filter(Function.module_id==record_id, Function.class_id==None):
        print fun
    
    return jsonify({"result": data, "classes": classes, "functions": functions})

@app.route('/list')
@init_global
def list(**kwargs):
    project_id = g.project_id
    keyword = request.args.get("term", "").lower()
    result = []
    search_class = search_module = search_function = True

    if keyword.startswith("m:"):
        keyword = keyword[2:].strip()
        search_class = search_function = False
    elif keyword.startswith("c:"):
        keyword = keyword[2:].strip()
        search_module = search_function = False
    elif keyword.startswith("f:"):
        keyword = keyword[2:].strip()
        search_module = search_class = False

    if search_module:
        moduldes = session.query(Module).filter(Module.name.like("%%%s%%"%keyword))[0:100]
        for m in moduldes:
            d = m.as_dict();
            d['label'] = m.name
            result.append(d)

    if search_class:
        classes = session.query(Class).options(joinedload('module')).filter(Class.name.like("%%%s%%"%keyword))[0:100]
        for c in classes:
            d = c.as_dict(code=False)
            d['label'] = "class %s"%c.name
            result.append(d)

    if search_function:
        functions = session.query(Function).options(joinedload('module'), joinedload('cls')).filter(Function.name.like("%%%s%%"%keyword))[0:100]
        for f in functions:
            d = f.as_dict(code=False)
            d['label'] = "%s()"%f.name
            result.append(d)

    for r in result:
        r['project_id'] = project_id
        r['distance'] = Levenshtein.distance(keyword, r['name'].lower())

    result = sorted(result, key=lambda x:x['distance'])[:20]
    return jsonify({"data": result})

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")
