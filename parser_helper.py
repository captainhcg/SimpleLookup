import sys
import settings
import sqlite3

__DB_NAME__ = ""
__DB_CONN__ = None
def getConn():
    global __DB_CONN__
    if __DB_CONN__ is None:
        print "open conn"
        __DB_CONN__ = sqlite3.connect('db/%s.db'%__DB_NAME__)
    return __DB_CONN__

def closeConn():
    global __DB_CONN__
    if __DB_CONN__:
        __DB_CONN__.close()

def reset(project_id=0):
    global __DB_NAME__
    __DB_NAME__ = settings.PROJECTS[project_id]["DB_NAME"]
    conn = getConn()
    # Create table
    c = conn.cursor()
    c.execute("""
        DROP TABLE IF EXISTS module;
        """)
    c.execute("""
        CREATE TABLE module(
            id INTEGER PRIMARY KEY      NOT NULL,
            name           CHAR(64)     NOT NULL,
            path           TEXT         NOT NULL
        )
        """)
    c.execute("""
        DROP TABLE IF EXISTS class;
        """)
    c.execute("""
        CREATE TABLE class(
            id INTEGER PRIMARY KEY      NOT NULL,
            name           CHAR(64)     NOT NULL,
            code           TEXT         NOT NULL,
            module_id      INTEGER,
            class_id       INTEGER,
            FOREIGN KEY(module_id) REFERENCES module(id)
            FOREIGN KEY(class_id) REFERENCES class(id)
        )
        """)
    c.execute("""
        DROP TABLE IF EXISTS function;
        """)
    c.execute("""
        CREATE TABLE function(
            id INTEGER PRIMARY KEY      NOT NULL,
            name           CHAR(64)     NOT NULL,
            code           TEXT         NOT NULL,
            module_id      INTEGER,
            class_id       INTEGER,
            function_id    INTEGER,
            FOREIGN KEY(module_id) REFERENCES module(id)
            FOREIGN KEY(class_id) REFERENCES class(id)
            FOREIGN KEY(function_id) REFERENCES function(id)
        )
        """)
    c.execute("""
        DROP TABLE IF EXISTS attribute;
        """)
    c.execute("""
        CREATE TABLE attribute(
            id INTEGER PRIMARY KEY      NOT NULL,
            name           CHAR(64)     NOT NULL,
            code           TEXT         NOT NULL,
            module_id      INTEGER,
            class_id       INTEGER,
            FOREIGN KEY(module_id) REFERENCES module(id)
            FOREIGN KEY(class_id) REFERENCES class(id)
        )
        """)
    conn.commit()

def addModule(name, path):
    last_id = 0
    conn = getConn()
    c = conn.cursor()
    c.execute(u"INSERT INTO module (name, path) VALUES ('%s','%s')"%(name, path))
    last_id = c.lastrowid
    conn.commit()
    return last_id

def setClassCode(class_id, code=""):
    conn = getConn()
    c = conn.cursor()
    c.execute(u"UPDATE class SET code = ? WHERE id = ?", (code, class_id))
    conn.commit()

def setFunctionCode(function_id, code=""):
    conn = getConn()
    c = conn.cursor()
    c.execute(u"UPDATE function SET code = ? WHERE id = ?", (code, function_id))
    conn.commit()   

def addAttribute(name, module_id, class_id, code=""):
    last_id = 0
    conn = getConn()
    c = conn.cursor()
    c.execute(u"INSERT INTO attribute (name, module_id, class_id, code) VALUES (?, ?, ?, ?)", (name, module_id or "NULL", class_id or "NULL", code))
    last_id = c.lastrowid
    conn.commit()
    return last_id

def addFunction(name, module_id, class_id, function_id, code=""):
    last_id = 0
    conn = getConn()
    c = conn.cursor()
    c.execute(u"INSERT INTO function (name, module_id, class_id, function_id, code) VALUES (?, ?, ?, ?, ?)", (name, module_id or "NULL", class_id or "NULL", function_id or "NULL", code))
    last_id = c.lastrowid
    conn.commit()
    return last_id

def addClass(name, module_id, class_id, code=""):
    last_id = 0
    conn = getConn()
    c = conn.cursor()
    c.execute(u"INSERT INTO class (name, module_id, class_id, code) VALUES (?, ?, ?, ?)", (name, module_id or "NULL", class_id or "NULL", code))
    last_id = c.lastrowid
    conn.commit()
    return last_id