from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db = SQLAlchemy()
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)




class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer)
    description = db.Column(db.String)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.Integer)
    img_url = db.Column(db.Integer)

with app.app_context():
    db.create_all()

"""
    new_movie = Movie(
        title="Phone Booth",
        year=2002,
        description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
        rating=7.3,
        ranking=10,
        review="My favourite character was the caller.",
        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    )
    all_movies = db.session.query(Movie).all()
    #db.session.add(new_movie)
    #db.session.commit()
"""

@app.route("/", methods=['GET', 'POST'])
def home():
    all_movies = db.session.query(Movie).order_by(Movie.rating).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i

    db.session.commit()
    return render_template("index.html", all_movies=all_movies)


class RateMovieForm(FlaskForm):
    edit_rating = FloatField('Your rating out of 10 .e.g. 7.5', validators=[DataRequired()])
    edit_review = StringField('Your review', validators=[DataRequired()])
    submit = SubmitField("Done")


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.edit_rating.data)
        movie.review = form.edit_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, movie=movie)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


class AddMovie(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()], render_kw={'style':  'width: 30ch'})
    submit = SubmitField("Add Movie")

api_key = '9ff47d8991bc5d4b8bf84d811fc9cdb3'

@app.route('/add', methods=["GET", "POST"])
def add():
    form = AddMovie()
    movie_title = form.title.data
    if request.method == 'POST':
        response = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}')
        tmdb = response.json()['results']
        return render_template('select.html', data=tmdb)
    return render_template('add.html', form=form)


@app.route('/find')
def find_movie():
    movie_api_id = request.args.get("id")
    print(movie_api_id)
    if movie_api_id:
        response2 = requests.get(f'https://api.themoviedb.org/3/movie/{movie_api_id}?api_key=9ff47d8991bc5d4b8bf84d811fc9cdb3')
        movie_by_id = response2.json()
        print(movie_by_id)
        new_movie1 = Movie(
            title=movie_by_id['original_title'],
            img_url=f'https://www.themoviedb.org/t/p/w1280{movie_by_id["poster_path"]}',
            year=movie_by_id['release_date'].split('-')[0],
            description=movie_by_id['overview'],
        )
        db.session.add(new_movie1)
        db.session.commit()
    return redirect(url_for('edit', id=new_movie1.id))


if __name__ == '__main__':
    app.run(debug=True)
