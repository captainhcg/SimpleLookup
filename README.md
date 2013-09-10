SimpleLookup
============

### Setup

* Install Required Packages: `sudo pip install -r requirements.txt`
  + Flask,  [A lightweight Python web framework](http://flask.pocoo.org/)
  + SQLalchemy, [The Database Toolkit for Python](http://www.sqlalchemy.org/)
  + python-Levenshtein, [Computing string distances for sorting](https://pypi.python.org/pypi/python-Levenshtein/)
  + Pygments, [Python Syntax Highlighter](http://pygments.org/)
  + pygments-style-github, [A port of the github color scheme for pygments](https://github.com/hugomaiavieira/pygments-style-github)

* Set up settings.py: 
  + Create setting file by renaming `settings.py.pk` to `settings.py` and
  + Set the 'NAME', 'DB_NAME' and 'PROJECT_PATH' of your project. 'NAME' and 'DB_NAME' can be arbitary string, 'PROJECT_PATH' must point to a valid python code base. For example `/usr/lib/python2.6/site-packages/flask/` or `/Users/user_name/vitualenvs/drc/lib/python2.7/site-packages/django/`

* Set up Databases
  + Execute `python parser.p --project=[project id]` or  `python parser.p --all` to parse project(s). If no argument is provided, the first project would be parsed.

### Run Server

* Just `python run.py` under project path. By default it uses 5000 port. 
* Take a look at [Simple Lookup](http://127.0.0.1:5000)
* 
not done yet...
