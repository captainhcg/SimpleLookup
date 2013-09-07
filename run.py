from flask import Flask, render_template, request, jsonify, g
from flask.ext.sqlalchemy import SQLAlchemy
import Levenshtein
import settings
from functools import wraps
import sqlite3
import sys, os

app = Flask(__name__)
projects=settings.PROJECTS

# alway pass project_id to view
def init_global(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        global app
        try:
            g.project_id = int(request.args.get('project_id', 2))
        except:
            g.project_id = 2
        
        db_name = settings.PROJECTS[g.project_id]["DB_NAME"]
        with sqlite3.connect(os.path.dirname(__file__)+'/db/%s.db'%db_name) as g.conn:
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
    conn = g.conn
    c = conn.cursor()
    c.execute("SELECT f.id, f.name, f.module_id, f.code, f.class_id, m.path, m.name, c.name FROM function as f INNER JOIN module AS m ON f.module_id = m.id LEFT JOIN class AS c ON f.class_id = c.id WHERE f.id = ?", (record_id, ))
    row = c.fetchone()
    record_type = "method" if row[4] else "function"
    data = {
        "id": row[0],
        "project_id": g.project_id,
        "name": row[1],
        "type": record_type,
        "module_id": row[2],
        "module_path": row[5],
        "module_name": row[6],
        "class_id": row[4],
        "class_name": row[7],
        "code": row[3]
    }
    return jsonify({"result": data})

def searchClass(query):
    project_id = g.project_id
    record_id = query.get('id')
    conn = g.conn
    c = conn.cursor()
    c.execute("SELECT c.id, c.name, c.module_id, c.code, m.path, m.name FROM class as c INNER JOIN module AS m ON c.module_id = m.id WHERE c.id = ?", (record_id, ))
    row = c.fetchone()
    data = {
        "id": row[0],
        "project_id": g.project_id,
        "name": row[1],
        "type": "class",
        "module_id": row[2],
        "module_path": row[4],
        "module_name": row[5],
        "code": row[3]
    }
    attrs = []
    for row in c.execute("SELECT id, name, code FROM attribute WHERE class_id = ? ORDER BY name", (record_id, )):
        attrs.append({
            "id": row[0],
            "name": row[1],
            "code": row[2].split("=", 1)[-1].strip()
        })
    functions = []
    for row in c.execute("SELECT f.id, f.name, f.module_id, f.class_id, m.path, m.name, c.name FROM function as f INNER JOIN module AS m ON f.module_id = m.id LEFT JOIN class AS c ON f.class_id = c.id WHERE f.class_id = ?", (record_id,)):
        record_type = "method"
        if row[6]:
            record_desc = "%s/%s.%s.%s()"%(row[4], row[5], row[6], row[1])
        else:
            record_desc = "%s/%s.%s()"%(row[4], row[5], row[1])
        functions.append({
            "id": row[0],
            "project_id": project_id,
            "name": row[1],
            "label": row[1]+"()",
            "desc": record_desc,
            "value": row[0],
            "type": record_type,
            "module": row[2],
            "class": row[3],
        })
    return jsonify({"result": data, "attrs": attrs, "functions": functions})

def searchModule(query):
    project_id = g.project_id
    record_id = query.get('id')
    conn = g.conn
    c = conn.cursor()
    c.execute("SELECT id, name, path FROM module WHERE id = ?", (record_id, ))
    row = c.fetchone()
    data = {
        "id": row[0],
        "project_id": project_id,
        "name": row[1],
        "label": row[1],
        "desc": "%s/%s.py"%(row[2], row[1]),
        "path": row[2],
        "type": "module",
    }

    classes = []
    for row in c.execute("SELECT c.id, c.name, c.module_id, m.path, m.name FROM class AS c INNER JOIN module AS m ON c.module_id = m.id WHERE m.id = ? AND c.class_id = 'NULL'", (record_id, )):
        classes.append({
            "id": row[0],
            "project_id": project_id,
            "name": row[1],
            "label": "class "+row[1],
            "desc": "%s/%s.%s"%(row[3], row[4], row[1]),
            "type": "class",
            "module_id": row[2],
            "module_path": row[3],
            "module_name": row[4],
        })

    functions = []
    for row in c.execute("SELECT f.id, f.name, f.module_id, f.class_id, m.path, m.name, c.name FROM function as f INNER JOIN module AS m ON f.module_id = m.id LEFT JOIN class AS c ON f.class_id = c.id WHERE f.class_id = 'NULL' AND f.module_id = ?", (record_id,)):
        record_type = "method"
        if row[6]:
            record_desc = "%s/%s.%s.%s()"%(row[4], row[5], row[6], row[1])
        else:
            record_desc = "%s/%s.%s()"%(row[4], row[5], row[1])
        functions.append({
            "id": row[0],
            "project_id": project_id,
            "name": row[1],
            "label": row[1]+"()",
            "desc": record_desc,
            "type": record_type,
            "module_id": row[2],
            "module_path": row[4],
            "module_name": row[5],
            "class_name": row[6],
            "class_id": row[3],
        })
    return jsonify({"result": data, "classes": classes, "functions": functions})

@app.route('/list')
@init_global
def list(**kwargs):
    project_id = g.project_id
    keyword = request.args.get("term", "").lower()
    conn = g.conn
    c = conn.cursor()
    result = []
    search_class = search_module = search_function = True

    if keyword.startswith("m:"):
        keyword = keyword[2:].strip()
        search_class = False
        search_function = False
    elif keyword.startswith("c:"):
        keyword = keyword[2:].strip()
        search_module = False
        search_function = False
    elif keyword.startswith("f:"):
        keyword = keyword[2:].strip()
        search_module = False
        search_class = False

    if search_module:
        for row in c.execute("SELECT id, name, path FROM module WHERE name LIKE ?", ("%"+keyword+"%", )):
            result.append({
                "id": row[0],
                "project_id": project_id,
                "name": row[1],
                "label": row[1],
                "desc": "%s/%s.py"%(row[2], row[1]),
                "type": "module",
                "distance": Levenshtein.distance(keyword, row[1].lower())
            })

    if search_class:
        for row in c.execute("SELECT c.id, c.name, c.module_id, m.path, m.name FROM class AS c INNER JOIN module AS m ON c.module_id = m.id WHERE c.name LIKE ?", ("%"+keyword+"%", )):
            result.append({
                "id": row[0],
                "project_id": project_id,
                "name": row[1],
                "label": "class "+row[1],
                "desc": "%s/%s.%s"%(row[3], row[4], row[1]),
                "type": "class",
                "module": row[2],
                "distance": Levenshtein.distance(keyword, row[1].lower())
            })

    if search_function:
        for row in c.execute("SELECT f.id, f.name, f.module_id, f.class_id, m.path, m.name, c.name FROM function as f INNER JOIN module AS m ON f.module_id = m.id LEFT JOIN class AS c ON f.class_id = c.id WHERE f.name LIKE ?", ("%"+keyword+"%", )):
            record_type = "method" if row[3] else "function"
            if row[6]:
                record_desc = "%s/%s.%s.%s()"%(row[4], row[5], row[6], row[1])
            else:
                record_desc = "%s/%s.%s()"%(row[4], row[5], row[1])
            result.append({
                "id": row[0],
                "project_id": project_id,
                "name": row[1],
                "label": row[1]+"()",
                "desc": record_desc,
                "type": record_type,
                "module": row[2],
                "class": row[3],
                "distance": Levenshtein.distance(keyword, row[1].lower())
            })
    result = sorted(result, key=lambda x:x['distance'])[:20]
    return jsonify({"data": result})

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")
