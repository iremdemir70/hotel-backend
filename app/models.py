from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    profile_image_url = db.Column(db.Text, nullable=True)
    is_google_user = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    comments = db.relationship('Comment', backref='user', lazy=True)

class Hotel(db.Model):
    __tablename__ = 'hotels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    location = db.Column(db.String(150))
    price = db.Column(db.Float)
    rating = db.Column(db.Float)
    image_url = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_flagged = db.Column(db.Boolean, default=False)
    discount_percent = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='hotel', lazy=True)
    amenities = db.relationship('HotelAmenity', backref='hotel', lazy=True)
    available_on_weekend = db.Column(db.Boolean, default=False)  # Dummy boolean örnek
    country = db.Column(db.String(100))
class Amenity(db.Model):
    __tablename__ = 'amenities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    hotels = db.relationship('HotelAmenity', backref='amenity', lazy=True)

class HotelAmenity(db.Model):
    __tablename__ = 'hotel_amenities'
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id', ondelete='CASCADE'))
    amenity_id = db.Column(db.Integer, db.ForeignKey('amenities.id', ondelete='CASCADE'))

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id', ondelete='CASCADE'))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    rating = db.relationship('Rating', backref='comment', uselist=False)

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'))
    cleanliness = db.Column(db.Float)
    service = db.Column(db.Float)
    facilities = db.Column(db.Float)
    location = db.Column(db.Float)
    eco_friendliness = db.Column(db.Float)


class HotelAvailability(db.Model):
    __tablename__ = 'hotel_availabilities'
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id', ondelete='CASCADE'))
    date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
