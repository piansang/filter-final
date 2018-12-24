import os
from datetime import timedelta
from flask import render_template, flash, request, send_from_directory, redirect, url_for, jsonify
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import *
from app.filter import filter_image, filter_and_thumbnail

UPLOAD_FOLDER = os.path.basename('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/filter")
def filter():
    return render_template("main.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            flash('Logged in successfully.')
            next_page = url_for('main')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/filter', methods=['POST'])
def upload_filter():
    # file = request.files['image']
    # choice = request.form['filter']
    # f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    # file.save(f)
    # new_file = filter.filter_image(file.filename, choice)
    # return render_template('main.html', filename = "/uploads/" + new_file)
    
    content = request.get_json()
    img = filter_image(content['image'], content['filter'])
    return jsonify(image=img)

@app.route('/upload', methods=['POST'])
def upload_profile():
    # file = request.files['image']
    # choice = request.form['filter']
    # f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    # file.save(f)
    # new_file = filter.filter_image(file.filename, choice)
    # return render_template('main.html', filename = "/uploads/" + new_file)
    
    content = request.get_json()
    result = filter_and_thumbnail(content['image'])
    post = Image(image=result[0], thumbnail=result[1], author=current_user)
    db.session.add(post)
    db.session.commit()
    flash("Image uploaded successfully.")
    return redirect(url_for('user', username=current_user.username))
    

@app.route('/uploadalbum', methods=['POST'])
def upload_album():
    # file = request.files['image']
    # choice = request.form['filter']
    # f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    # file.save(f)
    # new_file = filter.filter_image(file.filename, choice)
    # return render_template('main.html', filename = "/uploads/" + new_file)
    
    content = request.get_json()
    result = filter_and_thumbnail(content['image'])
    album = Album.query.get(content['album'])
    post = Image(image=result[0], thumbnail=result[1], author=current_user)
    db.session.add(post)
    album.add_image(post)
    db.session.commit()
    flash("Image uploaded successfully.")
    return redirect(url_for('user', username=current_user.username))

@app.route('/upload', methods=['GET'])
def upload():
    return redirect(url_for('filter'))

@app.route('/profile/<username>', methods=['GET'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    images = user.images.order_by(Image.timestamp.desc()).paginate(page, error_out=False)
    next_url = url_for('user', username=user.username, page=images.next_num) if images.has_next else None
    prev_url = url_for('user', username=user.username, page=images.prev_num) if images.has_prev else None
    return render_template('user.html', user=user, images=images.items, next_url = next_url, prev_url = prev_url, switch=True)
    
@app.route('/profile/<username>/albums', methods=['GET'])
@login_required
def user_albums(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    albums = user.albums.order_by(Album.timestamp.desc()).paginate(page, error_out=False)
    next_url = url_for('user', username=user.username, page=albums.next_num) if albums.has_next else None
    prev_url = url_for('user', username=user.username, page=albums.prev_num) if albums.has_prev else None
    return render_template('user.html', user=user, albums=albums.items, next_url = next_url, prev_url = prev_url, switch=False)

@app.route('/album/<id>', methods=['GET'])
def album_view(id):
    album = Album.query.get(id)
    print(album)
    return render_template('album_view.html', album=album)

@app.route('/album', methods=['GET'])
def album_create():
    current_time = datetime.utcnow()
    delta = current_time - timedelta(weeks=1)
    items = Image.query.filter(Image.timestamp > delta).all()
    return render_template('album_create.html', title='Albums', images=items)    

@app.route('/album', methods=['POST'])
def album_create_():
    images = request.form.get('images')
    title = request.form.get('title')
    print(title)
    print(type(title))
    new_album = Album(name=title, creator=current_user.id)
    db.session.add(new_album)
    db.session.commit()
    for id in images:
        new_album.add_images(Image.query.get(int(id)))
    flash("Album created successfully.")
    return redirect(url_for('main'))