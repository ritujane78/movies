from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
import os
from dotenv import load_dotenv
'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

movie_url = "https://api.themoviedb.org/3/search/movie"

load_dotenv()
api_key = os.getenv("API_KEY")

# CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE
class Movie(db.Model):
    id:Mapped[int]= mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    year: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    rating:Mapped[float] = mapped_column(Float, nullable=False)
    ranking:Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)


# with app.app_context():
#     db.create_all()
#
# with app.app_context():
#     new_movie = Movie(title="Phone Booth",year="2002",description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#                       rating=7.3,ranking=10,review="My favourite character was the caller.",
#                       img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#                       )
#
#     db.session.add(new_movie)
#     db.session.commit()


class AddForm(FlaskForm):
    movie_title = StringField("Movie Title", validators=[DataRequired()])
    add_button = SubmitField("Add Movie")


class EditForm(FlaskForm):
    new_rating = FloatField('Your Rating out of 10 e.g. 7.5')
    new_review = StringField("Your Review")
    edit_submit = SubmitField("Done")


@app.route("/", methods=['POST', 'GET'])
def home():
    query = db.session.execute(db.select(Movie))
    all_movies = query.scalars().all()
    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=['GET','POST'])
def add_movie():
    new_movie_add_form = AddForm()
    if request.method == 'POST':
        title = new_movie_add_form.movie_title.data
        response = requests.get(movie_url, params={"api_key": api_key, "query": title})
        movie_titles = response.json()

        return render_template("select.html", movie_list=movie_titles['results'])

    return render_template("add.html", form=new_movie_add_form)


@app.route("/edit", methods=['POST', 'GET'])
def edit_movie():
    movie_id = request.args.get('id')
    query = db.session.execute(db.select(Movie).where(Movie.id==movie_id))
    selected_movie = query.scalar()
    movie_edit_form = EditForm()
    if request.method=='POST':
        row_to_update = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
        if movie_edit_form.new_rating.data:
            row_to_update.rating = movie_edit_form.new_rating.data
        if movie_edit_form.new_review.data:
            row_to_update.review = movie_edit_form.new_review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", movie=selected_movie, form=movie_edit_form)


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get('id')
    print(movie_id)
    movie_to_delete = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect("/")



if __name__ == '__main__':
    app.run(debug=True)
