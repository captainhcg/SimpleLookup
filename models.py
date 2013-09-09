from settings import PROJECTS, SQLALCHEMY_ECHO
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, deferred, create_session
from sqlalchemy.ext.declarative import declarative_base

sessions = []
engines = []
for idx, project in enumerate(PROJECTS):
    engine = create_engine(PROJECTS[idx]['DB_URL'], echo=SQLALCHEMY_ECHO)
    engines.append(engine)
    sessions.append(create_session(bind=engine, autocommit=False))

engine = engines[0]
session = sessions[0]
Base = declarative_base()

class Module(Base):
    __tablename__ = 'module'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    path = Column(Text)
    code = deferred(Column(Text))
    lines = Column(Integer)

    classes = relationship("Class", backref="module")
    functions = relationship("Function", backref="module")

    def __init__(self, name=""):
        self.name = name

    def __repr__(self):
        return '<Module %r>' % self.name

    def save(self):
        session.add(self)
        session.commit()

    def as_dict(self, code=True):
        return {
            "id": self.id,
            "name": self.name,
            "label": "%s.py"%self.name,
            "desc": self.description,
            "type": "module",
            "lines": self.lines,
            "path": self.path,
            "code": self.code if code else ""
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

class Class(Base):
    __tablename__ = 'class'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    code = deferred(Column(Text))
    module_id = Column(Integer, ForeignKey('module.id'))
    parent_class_id = Column(Integer, ForeignKey('class.id'), nullable=True)

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
            "label": "class %s"%self.name,
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

class Function(Base):
    __tablename__ = 'function'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    code = deferred(Column(Text))
    module_id = Column(Integer, ForeignKey('module.id'))
    class_id = Column(Integer, ForeignKey('class.id'), nullable=True)
    parent_function_id = Column(Integer, ForeignKey('function.id'), nullable=True)

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
            "label": "%s()"%self.name,
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

class Attribute(Base):
    __tablename__ = 'attribute'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    code = Column(Text)
    module_id = Column(Integer, ForeignKey('module.id'))
    class_id = Column(Integer, ForeignKey('class.id'))

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
            "label": self.name,
            "value": self.code.split("=", 1)[-1].strip()
        }

    @staticmethod
    def addAttribute(name="", module_id=None, class_id=None):
        a = Attribute(name=name)
        a.module_id = module_id
        a.class_id = class_id
        a.save()
        return a

def setProject(project_id=0):
    global session, engine
    engine = engines[project_id]
    session = sessions[project_id]

def getSession(project_id=0):
    return sessions[project_id]

def resetDB():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    pass