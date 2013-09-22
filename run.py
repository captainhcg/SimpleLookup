#!/usr/bin/env python
from flask import Flask
from werkzeug.wsgi import DispatcherMiddleware
from search_app import app as entrance
from track_app import app as track
import settings

if __name__ == '__main__':
    app = Flask( __name__ )
    app.wsgi_app = DispatcherMiddleware(entrance.wsgi_app, {
        '/track': track.wsgi_app
    })

    app.run(
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        debug=True,
    )
