#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import add
from typing import final
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import flask
from flask.json import jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.sql.schema import MetaData
from werkzeug.exceptions import abort
from forms import *
from flask_migrate import Migrate, show
from datetime import date, datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2225@localhost:5432/fyyur'

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



def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():

  now = datetime.utcnow
  shows = Show.query.join(Venue , Venue.id == Show.venue_id).join(Artist , Artist.id == Show.artist_id).order_by(Show.id.desc()).limit(10).all()

  result = []
  for show in shows:
        
    record = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    }

    result.append(record)

  return render_template('pages/home.html' , shows=result , url='/')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  areas = Venue.query.distinct('city', 'state').all()

  results = []
  for area in areas:
      
      record = {
        "city": area.city,
        "state": area.state,
        "venues": Venue.query.filter(Venue.city == area.city ,Venue.state == area.state).all()
      }
      results.append(record)

  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }]
    
    }]
  
  return render_template('pages/venues.html', areas=results);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = request.form

  venues = Venue.query.filter(Venue.name.ilike(f'%{data["search_term"]}%')).all()
  response={
    "count": len(venues),
    "data": venues
  }

  #  response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id).first()

  now = datetime.utcnow()


  upcoming_shows = Show.query.join(Artist , venue.id == Show.venue_id).filter(Show.start_time > now).all()
  past_shows = Show.query.join(Artist , venue.id == Show.venue_id).filter(Show.start_time < now).all()

  upcoming_shows_list = [] 

  for upcoming in upcoming_shows:
        
        record = {
            "artist_id": upcoming.artist.id,
            "artist_name": upcoming.artist.name,
            "artist_image_link": upcoming.artist.image_link,
            "start_time": str(upcoming.start_time)
        }
        upcoming_shows_list.append(record)


  past_shows_list = []
  for past in past_shows:
        
        record = {
            "artist_id": past.artist.id,
            "artist_name": past.artist.name,
            "artist_image_link": past.artist.image_link,
            "start_time": str(past.start_time)
        }
        past_shows_list.append(record)


  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_talent_description,
    "image_link": venue.image_link,
    "past_shows": past_shows_list,
    "upcoming_shows": upcoming_shows_list,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data )

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  venue = ''
  try:

    data = request.form

    venue = Venue(name=data['name'] ,
                  city=data['city'] , 
                  state=data['state'],
                  address=data['address'], 
                  phone=data['phone'] , 
                  image_link=data['image_link'] ,
                  facebook_link=data['facebook_link'] , 
                  website=data['website'] , 
                  genres=data.getlist('genres') , 
                  seeking_talent=bool(data['seeking_talent']) , 
                  seeking_talent_description=data['talent_description'])

    db.session.add(venue)
    db.session.commit()
      # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
    db.session.close()

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    # Show.query.filter(Show.venue_id == venue_id).delete()
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("venue deleted")

  except:
    db.session.rollback()
    flash("could not delete venue")
    error = True
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  if error:
        abort(400)
  else:    
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  #   
  data = request.form
  
  artists = Artist.query.filter(Artist.name.ilike(f"%{data['search_term']}%")).all()

  for g in artists:
        print(g.genres)

  response={
    "count": len(artists),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


  artist = Artist.query.filter_by(id=artist_id).first()

  now = datetime.utcnow()

  upcoming_shows = Show.query.join(Venue , artist.id == Show.artist_id).filter(Show.start_time > now).all()
  past_shows = Show.query.join(Venue , artist.id == Show.artist_id).filter(Show.start_time < now).all()


  upcoming_shows_list = []

  for upcoming in upcoming_shows:
        
        record = {
              "venue_id": upcoming.venue.id,
              "venue_name": upcoming.venue.name,
              "venue_image_link": upcoming.venue.image_link,
              "start_time": str(upcoming.start_time)
        }
        upcoming_shows_list.append(record)

  past_shows_list = [] 

  for past in past_shows:
        
        record = {
            "venue_id": past.venue.id,
            "venue_name": past.venue.name,
            "venue_image_link": past.venue.image_link,
            "start_time": str(past.start_time)
        }
        past_shows_list.append(record)


  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone":  artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_venue_description,
    "image_link": artist.image_link,
    "past_shows": past_shows_list ,
    "upcoming_shows": upcoming_shows_list,
    "past_shows_count": len(past_shows_list),
    "upcoming_shows_count": len(upcoming_shows_list),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.filter_by(id=artist_id).first()

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    data = request.form
    
    is_seeking = False

    if(data['seeking_venue'] != 'True'):
          is_seeking = False
    else: 
      is_seeking = True
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.image_link = data['image_link']
    artist.name = data['name']
    artist.city = data['city']
    artist.state = data ['state']
    artist.phone = data['phone']
    artist.genres = data.getlist('genres')
    artist.facebook_link = data['facebook_link']
    artist.seeking_venue = is_seeking
    artist.seeking_venue_description = data['venue_description']
    artist.website = data['website']


    db.session.commit()
    flash("Artist Information Updated")
  except: 
    db.rollback()
    flash("Artist Information could not be updated")
  finally:
    db.session.close()
  


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>

  venue = Venue.query.filter_by(id=venue_id).first()

  print(form)
  venue = Venue.query.filter_by(id=venue_id).first()

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    data = request.form

    is_seeking = False

    if(data['seeking_talent'] != 'True'):
        is_seeking = False
    else: 
        is_seeking = True

    venue = Venue.query.filter_by(id=venue_id).first()
    venue.image_link = data['image_link']
    venue.name = data['name']
    venue.city = data['city']
    venue.state = data['state']
    venue.address = data['address']
    venue.phone = data['phone']
    venue.genres = data.getlist('genres')
    venue.facebook_link = data['facebook_link']
    venue.seeking_talent = is_seeking
    venue.seeking_talent_description = data['talent_description']
    venue.website = data['website']

    db.session.commit()
    flash('updated Success')
  except:
    db.session.rollback()
    flash('The venue could not be updated')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead

  # TODO: modify data to be the data object returned from db insertion

  data = request.form
  is_seeking = False

  if(data['seeking_venue'] != 'True'):
        is_seeking = False
  else: 
    is_seeking = True

  try:

    artist = Artist(name=data['name'], 
                    city=data['city'], 
                    state=data['state'],
                    phone=data['phone'],
                    genres=data.getlist('genres'),
                    website=data['website'],
                    image_link=data['image_link'],
                    facebook_link=data['facebook_link'],
                    seeking_venue= is_seeking,
                    seeking_venue_description=data['venue_description'])

    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
  finally:
    db.session.close()

  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.


  now = datetime.utcnow()

  shows = Show.query.join(Venue , Venue.id == Show.venue_id).join(Artist , Artist.id == Show.artist_id).filter(Show.start_time > now).all()
  result = []
  for show in shows:
        
    record = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    }

    result.append(record)
  
  print(result)
  return render_template('pages/shows.html', shows=result)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    data = request.form

    show = Show(artist_id=data['artist_id'] , venue_id=data['venue_id'] , start_time=data['start_time'])
    db.session.add(show)
    db.session.commit()
      # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')

  finally:
    db.session.close()

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
