#!/usr/bin/env python

# uwsgi --http 0.0.0.0:5000 --workers 4 -w app:app
from app import app
import settings
app.run(
    host=settings.APP_HOST,
    port=settings.APP_PORT,
    debug=True,
)
