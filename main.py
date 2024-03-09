import requests
from flask import Flask, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired
from config import API_KEY

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
    description: Mapped[str] = mapped_column(String(800), unique=True, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String(800), unique=True, nullable=False)
    img_url: Mapped[str] = mapped_column(String(800), nullable=False)


with app.app_context():
    db.create_all()


class MovieForm(FlaskForm):
    rating = IntegerField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    Submit = SubmitField("Submit")


class AddMovie(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    Submit = SubmitField("Add Movie")


movie_data = requests.get(API_KEY).json()


@app.route("/")
def home():
    result = db.session.execute(db.select(Movies).order_by(Movies.id))
    all_movies = result.scalars()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["POST", "GET"])
def edit():
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
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movies, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add")
def add():
    add_form = AddMovie()
    return render_template("add.html", form=add_form)


if __name__ == "__main__":
    app.run(debug=True)
