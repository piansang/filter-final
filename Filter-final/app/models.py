from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager

size = app.config['BASE64_URL_SIZE']

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    images = db.relationship('Image', backref='author', lazy='dynamic')
    albums = db.relationship('Album', backref='creator_id', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.Text())
    thumbnail = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.image)

album_list = db.Table('album_list', 
    db.Column('album_id', db.Integer, db.ForeignKey('album.id'), primary_key=True),
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'), primary_key=True)
)
        
class Album(db.Model):	
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    creator = db.Column(db.Integer, db.ForeignKey('user.id'))
    images = db.relationship('Image', 
							  secondary=album_list, 
							  lazy='dynamic', 
							  backref=db.backref('albums', lazy='dynamic') 
							 )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    def add_image(self, image):
        # if not self.in_album(image):
        self.images.append(image)

    def remove_image(self, image):
        # if self.in_album(image):
        self.images.remove(image)

@login_manager.user_loader
def get_user(user_id):
    return User.query.get(int(user_id))
