import datetime

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


class AddForm(FlaskForm):
    title = StringField(label='The blog post title', name="title", validators=[DataRequired()])
    subtitle = StringField(label='The subtitle', name="subtitle", validators=[DataRequired()])
    author = StringField(label="The author's name", name="author", validators=[DataRequired()])
    img_url = StringField(label='A URL for the background image', name="img_url", validators=[DataRequired()])
    body = CKEditorField(label='The body (the main content) of the post', name="body", validators=[DataRequired()])
    submit = SubmitField(label='SUBMIT POST')


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost)).scalars()
    posts = result.all()
    return render_template("index.html", all_posts=posts)


@app.route('/<post_id>')
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route('/new-post', methods=["GET", "POST"])
def add_new_post():
    today = date.today()
    formatted_date = f'{today.strftime("%B")} {today.day}, {today.year}'
    if request.method == 'POST':
        add_post = BlogPost(
            title=request.form.get("title"),
            subtitle=request.form.get("subtitle"),
            date=formatted_date,
            body=request.form.get("body"),
            author=request.form.get("author"),
            img_url=request.form.get("img_url")
        )
        with app.app_context():
            db.session.add(add_post)
            db.session.commit()
        return redirect('/')

    form = AddForm()
    return render_template("make-post.html", form=form)


@app.route('/edit-post/<post_id>', methods=["GET", "POST"])
def edit_post(post_id):

    if request.method == 'POST':
        with app.app_context():
            requested_post = db.get_or_404(BlogPost, post_id)
            requested_post.title = request.form.get("title")
            requested_post.subtitle = request.form.get("subtitle")
            requested_post.body = request.form.get("body")
            requested_post.author = request.form.get("author")
            requested_post.img_url = request.form.get("img_url")
            db.session.commit()
        return redirect(f'/edit-post/{post_id}')

    requested_post = db.get_or_404(BlogPost, post_id)
    form = AddForm(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        author=requested_post.author,
        img_url=requested_post.img_url,
        body=requested_post.body
    )
    return render_template("make-post.html", form=form, post=requested_post)


@app.route('/delete/<post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
