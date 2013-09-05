from flask import Flask, render_template, request, jsonify, g
import Levenshtein
import settings
import simplejson
from functools import wraps
import sqlite3

app = Flask(__name__)
projects=settings.PROJECTS

# alway pass project_id to view
def init_global(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        try:
            g.project_id = int(request.args.get('project_id', 2))
        except:
            g.project_id = 2
        print g.project_id
        db_name = settings.PROJECTS[g.project_id]["DB_NAME"]
        with sqlite3.connect('db/%s.db'%db_name) as g.conn:
            return function(*args, **kwargs)
    return wrap

@app.route('/')
def hello_world():
    return render_template('index.html', projects=projects)

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
                "name": row[1],
                "label": row[1],
                "desc": "module: %s"%row[2],
                "value": row[0],
                "type": "module",
                "distance": Levenshtein.distance(keyword, row[1].lower())
            })

    if search_class:
        for row in c.execute("SELECT c.id, c.name, c.module_id, m.path, m.name FROM class AS c INNER JOIN module AS m ON c.module_id = m.id WHERE c.name LIKE ?", ("%"+keyword+"%", )):
            print row
            result.append({
                "id": row[0],
                "name": row[1],
                "label": row[1],
                "desc": "class: %s/%s.%s"%(row[3], row[4], row[1]),
                "value": row[0],
                "type": "class",
                "module": row[2],
                "distance": Levenshtein.distance(keyword, row[1].lower())
            })

    if search_function:
        for row in c.execute("SELECT f.id, f.name, f.module_id, f.class_id, m.path, m.name, c.name FROM function as f INNER JOIN module AS m ON f.module_id = m.id INNER JOIN class AS c ON f.class_id = c.id WHERE f.name LIKE ?", ("%"+keyword+"%", )):
            record_type = "method" if row[3] else "function"
            result.append({
                "id": row[0],
                "name": row[1],
                "label": row[1],
                "desc": "%s: %s/%s.%s.%s()"%(record_type, row[4], row[5], row[6], row[1]),
                "value": row[0],
                "type": record_type,
                "module": row[2],
                "class": row[3],
                "distance": Levenshtein.distance(keyword, row[1].lower())
            })
    result = sorted(result, key=lambda x:x['distance'])[:20]
    return simplejson.dumps(result)

if __name__ == '__main__':
    app.debug = True
    app.run()
