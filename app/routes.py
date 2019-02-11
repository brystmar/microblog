# when connecting from a web browser, show the Hello World page
from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


@app.route('/')  # map the top-level URL to this function
@app.route('/index')  # also map the /index URL to this same function
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = LoginForm()
    if form_login.validate_on_submit():
        # show a flashing message when login info is submitted
        flash('Login requested for user {}, remember_me={}'.format(form_login.username.data, form_login.remember_me.data))
        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form_login)
