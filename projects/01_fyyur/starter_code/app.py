#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import Venue, Artist,  Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = (
        Venue.query.distinct(Venue.city,Venue.state).with_entities(Venue.id, Venue.name, Venue.state, Venue.city)
        .order_by(Venue.city, Venue.state)
        .all()
    )

  data =[]

  for index, venue in enumerate(venues):
        data.append({"city": venue.city, "state": venue.state, "venues": []})

        data[index]["venues"].append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": Show.query.filter(
                    db.and_(Show.venue_id == venue.id, Show.start_time > datetime.now())
                ).count(),
            }
        )


  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  response = {"count": 0, "data": []}

  search_term = request.form.get('search_term', '')
  venues =  (
    Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.ilike(f"%{search_term}%")).all()
    )

  response["count"] = len(venues)
  response["data"] = [{"id": venue.id, "name": venue.name} for venue in venues]

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  #get detail page for venue
  venue = Venue.query.get(venue_id)
 
  upcoming_shows = Show.query.filter_by(venue_id=venue_id).filter(Show.start_time > datetime.now()).all()
  past_shows = Show.query.filter_by(venue_id=venue_id).filter(Show.start_time < datetime.now()).all()

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  
  message = ''

  try:
    venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website_link = form.website_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
    )
      
    db.session.add(venue)
    db.session.commit()

    venue_name = form.name.data
    message = (f"Venue {venue_name} was successfully listed!")
  except:
    db.session.rollback()

    venue_name = form.name.data
    message = (f"An error occured. Venue {venue_name} could not be listed!")

  finally:
    db.session.close()
  flash(message)

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    db.session.delete(venue)
    db.session.commit()

    message = (f"Venue {venue.name} was successfully deleted.")

  except:
    db.session.rollback()
    message = (f"An error occurred. Venue {venue.name} could not be deleted.")

    
  finally: 
    db.session.close()

  flash(message)
  
  return (url_for("index"))

  
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = (Artist.query.with_entities(Artist.id, Artist.name).all())

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  response = {"count": 0, "data": []}

  search_term = request.form.get('search_term', '')
  artists =  (
    Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.ilike(f"%{search_term}%")).all()
    )

  response["count"] = len(artists)
  response["data"] = [{"id": artist.id, "name": artist.name} for artist in artists]
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if artist:
    upcoming_shows = Show.query.filter(Show.start_time > datetime.now()).filter(Show.artist_id == artist_id).all()

    past_shows = Show.query.filter(Show.start_time < datetime.now()).filter(Show.artist_id == artist_id).all()

    data = {'id': artist.id,
            'name': artist.name,
            'genres': artist.genres,
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'seeking_venue': artist.seeking_venue,
            'image_link': artist.image_link,
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
            }
  

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = (
        Artist.query.with_entities(Artist.name, Artist.id)
        .filter(Artist.id == artist_id)
        .one_or_none()
    )

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()

  try:
    db.session.query(Artist).filter(Artist.id == artist_id).update(
      {
        "name" : form.name.data,
        "city" : form.city.data,
        "state" : form.state.data,
        "phone" : form.phone.data,
        "genres" : form.genres.data,
        "image_link" : form.image_link.data,
        "facebook_link" : form.facebook_link.data,
        "website_link" : form.website_link.data,
        "seeking_venue" : form.seeking_venue.data,
        "seeking_description" : form.seeking_description.data
      }
    )
    db.session.commit()
    message = (f"Artist was successfully edited!")
  except:
    db.session.rollback()
    message = (f"An error occurred. Artist could not be edited.")
  finally:
    db.session.close()
  flash(message)

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  try:
    db.session.query(Venue).filter(Venue.id == venue_id).update(
                {
                    "name": form.name.data,
                    "city": form.city.data,
                    "state": form.state.data,
                    "address": form.address.data,
                    "phone": form.phone.data,
                    "image_link": form.image_link.data,
                    "facebook_link": form.facebook_link.data,
                    "website_link": form.website_link.data,
                    "seeking_talent": form.seeking_talent.data,
                    "seeking_description": form.seeking_description.data,
                    "genres": form.genres.data
                }
     )
    db.session.commit()
    message = (f"Venue was successfully edited!")
  except:
    db.session.rollback()
    message = (f"An error occurred. Venue could not be edited.")
  finally:
    db.session.close()
  flash(message)

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()

  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm()

  message = ''
  artist_name = form.name.data
  try:
    artist = Artist(
      name = artist_name,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
    message = (f"Artist {artist_name} was successfully listed!")
  except:
    db.session.rollback()
    message = (f"An error occured. Artist {artist_name} could not be listed!")
  finally:
    db.session.close()

  flash(message)

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.order_by(Show.start_time).all()

  for show in shows:
        data.append(
            {
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time
            }
        )

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm()
  message = ''
  try:
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )

    db.session.add(show)
    db.session.commit()
    message = "Show was successfully listed!"

  except :
    db.session.rollback()
    message = "An error occurred. Show could not be listed."

  finally:
    db.session.close()
  # on successful db insert, flash success
  flash(message)

  return render_template('pages/home.html')

def die(error_message):
    raise Exception(error_message)

def __str__(self):
        
    if self.venue:
        return '%s (%s)' %(self.id, self.venue.id)
    else:
        return '%s (%s)' %(self.id, self.imprint)

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
