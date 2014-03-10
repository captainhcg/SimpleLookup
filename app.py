from flask import Flask
from werkzeug.wsgi import DispatcherMiddleware
from search_app import app as entrance
from track_app import app as track
import settings

app = Flask( __name__ )
app.wsgi_app = DispatcherMiddleware(entrance.wsgi_app, {
    '/track': track.wsgi_app
})

