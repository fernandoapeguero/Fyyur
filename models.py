from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from config import SQLALCHEMY_DATABASE_URI 


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

migrate = Migrate(app , db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean() , nullable=False , default=False)
    seeking_talent_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean() , nullable=False , default=False)
    seeking_venue_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    
        __tablename__ = 'shows'

        id = db.Column(db.Integer() , primary_key=True)
        start_time = db.Column(db.DateTime())

        artist_id = db.Column(db.Integer() , db.ForeignKey('artist.id'))
        venue_id = db.Column(db.Integer() , db.ForeignKey('venue.id'))

        artist = db.relationship(Artist , backref=db.backref('shows' , cascade='all,delete'))
        venue = db.relationship(Venue , backref=db.backref('shows' , cascade='all,delete'))
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
