from flask import Flask, render_template, request, jsonify
import Levenshtein
import settings
from functools import wraps
import sqlite3

app = Flask(__name__)
projects=settings.PROJECTS

def identify_project(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        try:
            project_id = request.args.get('project_id', 0)
        except:
            project_id = 0
        kwargs['project_id'] = int(project_id)
        return function(*args, **kwargs)
    return wrap

@app.route('/')
def hello_world():
    return render_template('index.html', projects=projects)

@app.route('/list')
@identify_project
def list(**kwargs):
    project_id = kwargs.get("project_id")
    keyword = request.args.get("keyword", "")
    conn = create_db_conn(project_id)
    c = conn.cursor()
    result = []
    for row in c.execute("SELECT id, name, module_id FROM class WHERE name LIKE ? LIMIT 100", ("%"+keyword+"%", )):
        result.append({
            "id": row[0],
            "name": row[1],
            "type": "class",
            "module": row[2],
            "distance": Levenshtein.distance(keyword, row[1])
        })
    print result
    return jsonify({"data": result})

def create_db_conn(project_id=0):
    DB_NAME = settings.PROJECTS[project_id]["DB_NAME"]
    return sqlite3.connect('db/%s.db'%DB_NAME)

if __name__ == '__main__':
    app.debug = True
    app.run()
