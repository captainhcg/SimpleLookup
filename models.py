from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from settings import PROJECTS, SQLALCHEMY_BINDS, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_ECHO
from sqlalchemy.orm import relationship, backref, deferred

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ECHO'] = SQLALCHEMY_ECHO
db = SQLAlchemy(app)
session = db.session

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    path = db.Column(db.Text)

    classes = relationship("Class", backref="module")
    functions = relationship("Function", backref="module")

    def __init__(self, name=""):
        self.name = name

    def __repr__(self):
        return '<Module %r>' % self.name

    def save(self):
        session.add(self)
        session.commit()

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "desc": self.description,
            "type": "module",
        }

    @property
    def description(self):
        return "%s/%s.py"%(self.path, self.name)

    @staticmethod
    def addModule(name="", path=""):
        m = Module(name=name)
        m.path = path
        m.save()
        return m

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    code = deferred(db.Column(db.Text))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    parent_class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)

    sub_class = relationship("Class", backref="parent_class", remote_side=[id])
    methods = relationship("Function", backref="cls")
    attributes = relationship("Attribute", backref="cls")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Class %r>' % self.name

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "desc": self.description,
            "type": "class",
        }

    def save(self):
        session.add(self)
        session.commit()

    def as_dict(self, code=True):
        return {
            "id": self.id, 
            "name": self.name,
            "desc": self.description,
            "type": "class",
            "code": self.code if code else "",
            "module_id": self.module.id,
            "module_name": self.module.name,
            "module_path": self.module.path,
        }

    @property
    def description(self):
        return "%s/%s.%s"%(self.module.path, self.module.name, self.name)

    @staticmethod
    def addClass(name="", module_id=None, class_id=None):
        c = Class(name=name)
        c.module_id = module_id
        c.parent_class_id = class_id
        c.save()
        return c

class Function(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    code = deferred(db.Column(db.Text))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)
    parent_function_id = db.Column(db.Integer, db.ForeignKey('function.id'), nullable=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Function %r>' % self.name

    def save(self):
        session.add(self)
        session.commit()

    @property
    def description(self):
        if self.class_id:
            return "%s/%s.%s.%s()"%(self.module.path, self.module.name, self.cls.name, self.name)
        else:
            return "%s/%s.%s()"%(self.module.path, self.module.name, self.name)  

    def as_dict(self, code=True):
        return {
            "id": self.id, 
            "name": self.name,
            "desc": self.description,
            "type": "function" if not self.class_id else "method",
            "code": self.code if code else "",
            "module_id": self.module.id,
            "module_name": self.module.name,
            "module_path": self.module.path,
            "class_id": self.class_id,
            "class_name": self.cls.name if self.class_id else "",
        }

    @staticmethod
    def addFunction(name="", module_id=None, class_id=None, function_id=None):
        f = Function(name=name)
        f.module_id = module_id
        f.class_id = class_id
        f.parent_function_id = function_id
        f.save()
        return f

class Attribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    code = db.Column(db.Text)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Attribute %r>' % self.name

    def save(self):
        session.add(self)
        session.commit()

    def as_dict(self):
        return {
            "id": self.id, 
            "name": self.name,
            "code": self.code,
        }

    @staticmethod
    def addAttribute(name="", module_id=None, class_id=None):
        a = Attribute(name=name)
        a.module_id = module_id
        a.class_id = class_id
        a.save()
        return a

def setProject(project_id=0):
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_BINDS[str(project_id)]

def resetDB():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    pass