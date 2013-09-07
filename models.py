from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from settings import PROJECTS, SQLALCHEMY_BINDS, SQLALCHEMY_DATABASE_URI

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    path = db.Column(db.Text)

    def __init__(self, name=""):
        self.name = name

    def __repr__(self):
        return '<Module %r>' % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def addModule(name="", path=""):
        m = Module(name=name)
        m.path = path
        m.save()
        return m

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    code = db.Column(db.Text)
    module = db.Column(db.Integer, db.ForeignKey('module.id'))
    cls = db.Column(db.Integer, db.ForeignKey('class.id'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Class %r>' % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def addClass(name="", module_id=None, class_id=None):
        c = Class(name=name)
        c.module = module_id
        c.cls = class_id
        c.save()
        return c

class Function(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    code = db.Column(db.Text)
    module = db.Column(db.Integer, db.ForeignKey('module.id'))
    cls = db.Column(db.Integer, db.ForeignKey('class.id'))
    fun = db.Column(db.Integer, db.ForeignKey('function.id'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Function %r>' % self.function

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def addFunction(name="", module_id=None, class_id=None, function_id=None):
        f = Function(name=name)
        f.module = module_id
        f.cls = class_id
        f.fun = function_id
        f.save()
        return f

class Attribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    code = db.Column(db.Text)
    module = db.Column(db.Integer, db.ForeignKey('module.id'))
    cls = db.Column(db.Integer, db.ForeignKey('class.id'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Attribute %r>' % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def addAttribute(name="", module_id=None, class_id=None):
        a = Attribute(name=name)
        a.module = module_id
        a.cls = class_id
        a.save()
        return a

def setProject(project_id=0):
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_BINDS[str(project_id)]

def resetDB():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    pass