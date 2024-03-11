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
    rating, assigns a ranking based on their order, and then renders them on the
    index.html template.
    :return: The `home()` function is returning a rendered template "index.html"
    with a list of movies sorted by their ratings. The function retrieves all
    movies from the database, orders them by their ratings, assigns a ranking to
    each movie based on its position in the sorted list, and then commits the
    changes to the database. Finally, it passes the list of movies to the
    "index.html" template for rendering
    """
    result = db.session.execute(db.select(Movies).order_by(Movies.rating)).scalars()
    all_movies = result.scalars().all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["POST", "GET"])
def edit():
    """
    This Python function edits a movie's rating and review in a database and
    redirects to the home page upon successful submission.
    :return: The `edit()` function is returning a rendered template "edit.html"
    along with the form and movie data.
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
    route using `url_for("home")`.
    """
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movies, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["POST", "GET"])
def add():
    """
    The function `add()` retrieves movie search results based on user input and
    renders a template with the search options.
    :return: The code snippet is returning either the rendered template
    "select.html" with the movie search results data if the form is validated and
    submitted successfully, or it is returning the rendered template "add.html"
    with the form for adding a movie if the form is not yet submitted or validated.
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
    The `find_movie` function retrieves movie data from an API based on an ID,
    creates a new movie object with the retrieved data, and redirects to an edit
    page for the new movie.
    :return: The code snippet is returning a redirect response to the "edit" route
    with the id of the newly added movie (new_movie.id).
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
