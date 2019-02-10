# when connecting from a web browser, show the Hello World page
from flask import render_template
from app import app

# map the top-level URL to this function
@app.route('/')
# also map the /index URL to this same function
@app.route('/index')

# specify what to return
def index():
    user = {'username': 'tberg'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Seattle!'
        },
        {
            'author': {'username': 'Susan'},
            'body':   'I love the TV show "I\'m Sorry"'
        }
    ]

    return render_template('index.html', title='Home', user=user, posts=posts)
