import sys, os

FILE_EXTENSION = ".py"

DB_ENGINE = "sqlite"
DB_PATH = os.path.dirname(__file__)+"/databases/"

PROJECTS = [
    {
        "NAME": "Simple Lookup",
        "DB_NAME": "SimpleLookup.sqlite",
        "PROJECT_PATH": ".",
    },
    {
        "NAME": "Django",
        "DB_NAME": "DJANGO.sqlite",
        "PROJECT_PATH": "/Users/che/vitualenvs/drc/lib/python2.7/site-packages/django/",
    },
    {
        "NAME": "Flask",
        "DB_NAME": "FLASK.sqlite",
        "PROJECT_PATH": "/Users/che/vitualenvs/drc/lib/python2.7/site-packages/flask/"
    },
    {
        "NAME": "SQLAlchemy",
        "DB_NAME": "SQLALCHEMY.sqlite",
        "PROJECT_PATH": "/Users/che/vitualenvs/drc/lib/python2.7/site-packages/sqlalchemy/"
    },
    {
        "NAME": "drchrono",
        "DB_NAME": "DRCHRONO.sqlite",
        "PROJECT_PATH": "/Users/che/Documents/drchrono-web/",
        "FOLDER_EXCLUDE_PATTERNS": ['migrations', 'chronometer_unit_tests']
    },  
]

for p in PROJECTS:
    p['DB_URL'] = DB_ENGINE + ":///" + DB_PATH + p['DB_NAME']

SQLALCHEMY_ECHO = False
