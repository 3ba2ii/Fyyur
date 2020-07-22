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
import sys
import time
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String())
    state = db.Column(db.String())
    address = db.Column(db.String())
    phone = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(
    ), default="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60")
    facebook_link = db.Column(db.String())
    website = db.Column(db.String(), nullable=True,)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=True)
    seeking_description = db.Column(
        db.String(), default='Not currently seeking for talents', nullable=True,)

    # 1 to Many relationship as the venue may have multiple shows,
    # that further will be distributed to upcoming and past shows
    venue_shows = db.relationship('Show', backref='venue-shows', lazy=True)

    # DONE:: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String())
    state = db.Column(db.String())
    phone = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(),
                           default="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60")
    facebook_link = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=True, nullable=True)
    seeking_description = db.Column(db.String(),
                                    default="Looking for shows to perform at any place in USA!",
                                    nullable=True)
    website = db.Column(db.String(), nullable=True,)

    # 1 to Many relationship as the artist may have multiple shows,
    # that further will be distributed to upcoming and past shows
    artist_shows = db.relationship('Show', backref='artist-shows', lazy=True)

    # Done: implement any missing fields, as a database migration using Flask-Migrate

# DONE: Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), nullable=False,)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')

# SECTION HELPERS


def distribute_shows(venue_shows):
    upcoming_shows, past_shows = [], []
    for show_id in venue_shows:
        show_date = Show.query.filter_by(
            id=show_id.id).first().start_time
        show_date = (str(show_date).split())[0]
        show_date = time.mktime(
            datetime.datetime.strptime(show_date, "%Y-%m-%d").timetuple())
        if Show.query.filter_by(id=show_id.id).first().start_time > datetime.datetime.utcnow():
            upcoming_shows.append(show_id)
        else:
            past_shows.append(show_id)
    return upcoming_shows, past_shows


def format_artist_shows(shows):
    result = []
    for show in shows:
        temp = {}
        temp['venue_id'] = show.venue_id
        temp['start_time'] = format_datetime(str(show.start_time))
        venue = Venue.query.get(show.venue_id)
        temp['venue_name'] = venue.name
        temp['venue_image_link'] = venue.image_link
        result.append(temp)
    return result
#  SECTION Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    received_venues = Venue.query.all()
    data = {}
    for venue in received_venues:
        upcoming_shows, past_shows = distribute_shows(venue.venue_shows)

        if venue.state not in data:
            data[venue.state] = {'city': venue.city, 'state': venue.state, 'venues': [{
                'id': venue.id, 'name': venue.name, 'num_upcoming_shows': len(upcoming_shows)}]}
        else:
            data[venue.state]['venues'].append({
                'id': venue.id, 'name': venue.name, 'num_upcoming_shows': len(upcoming_shows)
            })

    print(data.values())

    return render_template('pages/venues.html', areas=data.values())


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()
    upcoming_shows, past_shows = distribute_shows(venue.venue_shows)

    past = []
    upcoming = []
    for show in past_shows:
        past_show = {}
        past_show['artist_id'] = show.artist_id
        selected_artist = Artist.query.get(show.artist_id)
        past_show['artist_name'] = selected_artist.name
        past_show['start_time'] = format_datetime(
            str(show.start_time))
        past_show['artist_image_link'] = selected_artist.image_link
        past.append(past_show)

    for show in upcoming_shows:
        future = {}
        future['artist_id'] = show.artist_id
        selected_artist = Artist.query.get(show.artist_id)
        future['artist_name'] = selected_artist.name
        future['start_time'] = format_datetime(str(show.start_time))
        future['artist_image_link'] = selected_artist.image_link

        upcoming.append(future)
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
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past,
        "upcoming_shows": upcoming,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
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
    data = {}
    try:
        for key, value in request.form.items():
            if key == 'genres':
                continue
            elif key == 'seeking_talent':
                if value.lower() == 'yes':
                    data['seeking_talent'] = True
                else:
                    data['seeking_talent'] = False
            else:
                data[key] = value
        data['genres'] = request.form.getlist('genres')
        venue = Venue(name=data['name'],
                      city=data['city'], state=data['state'],
                      address=data['address'],
                      phone=data['phone'],
                      facebook_link=data['facebook_link'],
                      image_link=data['image_link'],
                      website=data['website'],
                      seeking_talent=data['seeking_talent'],
                      genres=data['genres'])
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + data['name'] + ' was successfully listed!')

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              data['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.with_entities(Artist.id, Artist.name).all()

    data = [{'id': artist.id, 'name': artist.name} for artist in artists]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    upcoming_shows, past_shows = distribute_shows(artist.artist_shows)
    upcoming, past = format_artist_shows(
        upcoming_shows), format_artist_shows(past_shows)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past,
        "upcoming_shows": upcoming,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    data = {}
    try:
        for key, value in request.form.items():
            if key == 'genres':
                continue
            elif key == 'seeking_venue':
                if value.lower() == 'yes':
                    data['seeking_venue'] = True
                else:
                    data['seeking_venue'] = False
            else:
                data[key] = value
        data['genres'] = request.form.getlist('genres')
        print('-'*80)
        print(data)
        print('-'*80)

        artist = Artist(name=data['name'],
                        city=data['city'], state=data['state'],
                        phone=data['phone'],
                        facebook_link=data['facebook_link'],
                        image_link=data['image_link'],
                        website=data['website'],
                        seeking_venue=data['seeking_venue'],
                        genres=data['genres'], seeking_description=data['seeking_description'])
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + data['name'] + ' was successfully listed!')

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' +
              data['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()

    data = [{'venue_id': show.venue_id, 'artist_id': show.artist_id,
             'start_time': format_datetime((str(show.start_time)))} for show in shows]
    for item in data:
        artist = Artist.query.get(item['artist_id'])
        item['artist_name'] = artist.name
        item['artist_image_link'] = artist.image_link
        item['venue_name'] = Venue.query.get(item['venue_id']).name
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    body = request.form
    print(body)
    try:
        show = Show(start_time=body['start_time'],
                    artist_id=body['artist_id'], venue_id=body['venue_id'])
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('Something went wrong please try again!')

    finally:
        db.session.close()

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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
