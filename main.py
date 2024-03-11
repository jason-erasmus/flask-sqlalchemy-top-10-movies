import requests
from flask import Flask, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from wtforms import FloatField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired

from config import API_IMG_URL, API_KEY, API_SEARCH_URL, API_URL

app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE
class Movies(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(
        String(800),
        nullable=False,
    )
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(800), nullable=True)
    img_url: Mapped[str] = mapped_column(String(800), nullable=False)


with app.app_context():
    db.create_all()


class MovieForm(FlaskForm):
    rating = FloatField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AddMovie(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    """
    The `home` function retrieves all movies from the database, orders them by
    rating, assigns a ranking to each movie, and then renders an HTML template with
    the list of movies.
    :return: The `home()` function is returning a rendered template "index.html"
    with a list of all movies fetched from the database, sorted by their ratings.
    The function updates the ranking of each movie based on its position in the
    sorted list before committing the changes to the database.
    """
    result = db.session.execute(db.select(Movies).order_by(Movies.rating)).scalars()
    all_movies = result.scalars().all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) -1
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["POST", "GET"])
def edit():
    """
    The `edit` function in Python retrieves a movie from the database, allows for
    editing its rating and review, and then updates the database with the changes.
    :return: The `edit()` function is returning a rendered template "edit.html"
    along with the form and movie data to be displayed on the webpage.
    """
    form = MovieForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movies, movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form, movie=movie)


@app.route("/delete", methods=["POST", "GET"])
def delete():
    """
    The `delete` function deletes a movie record from the database based on the
    provided movie ID and redirects to the home page.
    :return: The `delete()` function is returning a redirect response to the "home"
    route using `url_for("home")`. This means that after deleting the movie from
    the database and committing the changes, the user will be redirected to the
    "home" page.
    """
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movies, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["POST", "GET"])
def add():
    """
    The `add` function in Python uses a form to search for movie titles using an
    API and returns the search results in a template.
    :return: The code snippet is a Python function named `add()` that seems to be
    part of a Flask application. It appears to handle a form submission for adding
    a movie.
    """
    form = AddMovie()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(
            API_SEARCH_URL, params={"api_key": API_KEY, "query": movie_title}
        )
        data = response.json()["results"]
        return render_template("select.html", options=data)
    return render_template("add.html", form=form)


@app.route("/find")
def find_movie():
    """
    The `find_movie` function retrieves movie data from an API, creates a new movie
    object, and adds it to the database.
    :return: The `find_movie` function is returning a redirect response to the
    "edit" route with the `id` parameter set to the `id` of the newly added movie
    (`new_movie.id`).
    """
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_url = f"{API_URL}/{movie_api_id}"
        response = requests.get(movie_url, params={"api_key": API_KEY})
        data = response.json()
        new_movie = Movies(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            description=data["overview"],
            img_url=f"{API_IMG_URL}{data["poster_path"]}",
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit",id=new_movie.id))


if __name__ == "__main__":
    app.run(debug=True)
