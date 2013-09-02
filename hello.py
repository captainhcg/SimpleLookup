from flask import Flask, render_template
import settings

app = Flask(__name__)

@app.route('/')
def hello_world():
    projects=settings.PROJECTS
    return render_template('index.html', projects=projects)

if __name__ == '__main__':
    app.debug = True
    app.run()
