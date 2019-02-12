# when connecting from a web browser, show the Hello World page
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.route('/')  # map the top-level URL to this function
@app.route('/index')  # also map the /index URL to this same function
@login_required  # require login to view this page
# specify what to return
def index():
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

    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if a user is already logged in, redirect them to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()  # returns only the first result
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        # grab the user's desired page from the querystring
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':  # no requested next page, or that URL is suspicious
            next_page = url_for('index')
        return redirect(next_page)  # redirect to this desired page after login

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # if a user is already logged in, they don't need to see the registration page
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!  Please sign in.')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)
