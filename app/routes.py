# determines which page(s) to show for each browser request
import json
from flask import render_template, flash, redirect, url_for, request, g, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from werkzeug.urls import url_parse
from datetime import datetime

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post
from app.email import send_password_reset_email
from app.translate import translate


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@app.route('/', methods=['GET', 'POST'])  # map the top-level URL to this function
@app.route('/index', methods=['GET', 'POST'])  # also map the /index URL to this same function
@login_required  # require login to view this page
def index():
    form = PostForm()

    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''

        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Post created!'))
        return redirect(url_for('index'))

    current_page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        current_page, app.config['POSTS_PER_PAGE'], False)
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None

    return render_template('index.html', title=_('Home'), form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/explore')
@login_required
def explore():
    current_page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        current_page, app.config['POSTS_PER_PAGE'], False)
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None

    return render_template('index.html', title=_('Explore'), posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if a user is already logged in, redirect them to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()  # returns only the first result
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        # grab the user's desired page from the querystring
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':  # no requested next page, or if that URL is suspicious
            next_page = url_for('index')
        return redirect(next_page)  # redirect to this desired page after login

    return render_template('login.html', title=_('Sign In'), form=form)


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
        flash(_('Registration successful!  Please sign in.'))
        return redirect(url_for('login'))

    return render_template('register.html', title=_('Register'), form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()  # if user isn't found, return a 404 error

    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None

    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash(_('Changes saved.'))
        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':  # pre-populate the form if data already exists
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))

    if user == current_user:
        flash(_('You can\'t follow yourself!'))
        return redirect(url_for('user', username=username))

    current_user.follow(user)
    db.session.commit()
    flash(_('Now following %(username)s', username=username))

    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))

    if user == current_user:
        flash(_('You can\'t unfollow yourself!'))
        return redirect(url_for('user', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))

    return redirect(url_for('user', username=username))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title=_('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user = User.verify_reset_password_token(token)

    if not user:
        return redirect(url_for('index'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))

    return render_template('reset_password.html', form=form)


@app.route('/translate', methods=['GET', 'POST'])
def translate_text():
    result = translate(request.form['text'], request.form['source_language'], request.form['dest_language'])
    return jsonify({'text': result})
