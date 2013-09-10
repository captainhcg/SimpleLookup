SimpleLookup
============

### Setup

* Install Required Packages: `sudo pip install -r requirements.txt`
  + Flask,  [A lightweight Python web framework](http://flask.pocoo.org/)
  + SQLalchemy, [The Database Toolkit for Python](http://www.sqlalchemy.org/)
  + python-Levenshtein, [Computing string distances for sorting](https://pypi.python.org/pypi/python-Levenshtein/)
  + Pygments, [Python Syntax Highlighter](http://pygments.org/)
  + pygments-style-github[A port of the github color scheme for pygments](https://github.com/hugomaiavieira/pygments-style-github)

* Set up settings.py: 
  + Create setting file by renaming `settings.py.pk` to `settings.py`
  + Set the 'NAME', 'DB_NAME' and 'PROJECT_PATH' of your project. 'NAME' and 'DB_NAME' can be arbitary string, 'PROJECT_PATH' must point to a valid python code base. For example `/usr/lib/python2.6/site-packages/flask/` or `/Users/user_name/vitualenvs/drc/lib/python2.7/site-packages/django/`

* Set up Databases
  + Execute `python parser.py [number]`

not done yet...
