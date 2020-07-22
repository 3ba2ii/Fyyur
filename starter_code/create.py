app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


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
