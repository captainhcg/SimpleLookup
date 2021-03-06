from flask import render_template, request, jsonify, g
from flask.ext.assets import Environment, Bundle
import Levenshtein
import settings
from functools import wraps
from models import Module, Class, Function
from models import setProject, getSession
from sqlalchemy.orm import joinedload
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from search_app import app

projects = settings.PROJECTS
assets = Environment(app)
common_js = Bundle(
    'js/jquery.notify.min.js',
    Bundle(
        'js/simplelookup.coffee',
        filters='coffeescript'
    ),
    output='common_js.js'
)
assets.register('common_js', common_js)
common_css = Bundle('css/style.css', output='common_css.css')
assets.register('common_css', common_css)


def init_global(function):
    """alway pass project_id to view"""
    @wraps(function)
    def wrap(*args, **kwargs):
        global app
        try:
            g.project_id = int(request.args.get('project_id', 0))
        except:
            g.project_id = 0
        setProject(g.project_id)
        g.session = getSession(g.project_id)
        return function(*args, **kwargs)
    return wrap


@app.route('/')
def index():
    try:
        return render_template('index.html', projects=projects)
    except Exception, e:
        print e


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
    fun = g.session.query(Function).get(record_id)
    code = highlight(fun.code, PythonLexer(), HtmlFormatter(style='github', linenos='table'))
    data = fun.as_dict()
    methods = []
    functions = []
    attrs = []
    if fun.class_id:
        cls = fun.cls
        for attr in sorted(cls.attributes, key=lambda x: x.name):
            attrs.append(attr.as_dict())
        methods = []
        for method in sorted(cls.methods, key=lambda x: x.name):
            methods.append(method.as_dict(code=False))
    else:
        module = fun.module
        for fun in g.session.query(Function).filter(Function.module_id == module.id, Function.class_id == None).order_by(Function.name):
            functions.append(fun.as_dict(code=False))
    for li in (attrs, functions, methods):
        for item in li:
            item['project_id'] = g.project_id
    return jsonify({"record": data, "code": code, "attrs": attrs, "functions": functions, "methods": methods})


def searchClass(query):
    record_id = query.get('id')
    cls = g.session.query(Class).get(record_id)
    code = highlight(cls.code, PythonLexer(), HtmlFormatter(style='github', linenos='table'))
    data = cls.as_dict(code=False)
    attrs = []
    for attr in sorted(cls.attributes, key=lambda x: x.name):
        attrs.append(attr.as_dict())
    methods = []
    for method in sorted(cls.methods, key=lambda x: x.name):
        methods.append(method.as_dict(code=False))
    for li in (attrs, methods):
        for item in li:
            item['project_id'] = g.project_id
    return jsonify({"record": data, "code": code, "attrs": attrs, "methods": methods})


def searchModule(query):
    record_id = query.get('id')
    module = g.session.query(Module).get(record_id)
    data = module.as_dict(code=False)
    classes = []
    for cls in sorted(module.classes, key=lambda x: x.name):
        if not cls.parent_class_id:
            classes.append(cls.as_dict())

    functions = []
    for fun in g.session.query(Function).filter(Function.module_id == record_id, Function.class_id == None).order_by(Function.name):
        functions.append(fun.as_dict())

    if module.lines > 5000:
        code = "\n".join(module.code.split("\n")[:5001])
    code = highlight(module.code, PythonLexer(), HtmlFormatter(style='github', linenos='table'))
    for li in (classes, functions):
        for item in li:
            item['project_id'] = g.project_id
    return jsonify({"record": data, "code": code, "classes": classes, "functions": functions})


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
        moduldes = g.session.query(Module).filter(Module.name.like("%%%s%%" % keyword))[0:100]
        for m in moduldes:
            d = m.as_dict()
            result.append(d)

    if search_class:
        classes = g.session.query(Class).options(joinedload('module')).filter(Class.name.like("%%%s%%" % keyword))[0:100]
        for c in classes:
            d = c.as_dict(code=False)
            result.append(d)

    if search_function:
        functions = g.session.query(Function).options(joinedload('module'), joinedload('cls')).filter(Function.name.like("%%%s%%" % keyword))[0:100]
        for f in functions:
            d = f.as_dict(code=False)
            result.append(d)

    for r in result:
        r['project_id'] = project_id
        r['distance'] = Levenshtein.distance(keyword, r['name'].lower())

    result = sorted(result, key=lambda x: x['distance'])[:20]
    return jsonify({"data": result})
