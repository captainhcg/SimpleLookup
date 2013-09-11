#!/usr/bin/env python
from search_app import app
import settings

if __name__ == '__main__':
    app.static_folder = settings.PROJECT_PATH + "/static"
    app.run(
        host=settings.APP_HOST, 
        port=settings.APP_PORT, 
        debug=True,
    )
