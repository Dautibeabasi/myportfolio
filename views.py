from ast import Return
import email
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from requests import post
from .models import Note, User
from webforms import SearchForm
from . import db
import json
from flask_mail import Mail, Message
from config import mail_username

views = Blueprint("views", __name__)
mail = Mail()


@views.route("/")
def home():
    return render_template("index.html", user1=" Faith Ifeyemi Sobanke", user=current_user)


@views.route("/about")
def about():
    return render_template("about.html", user=current_user)


@views.route("/projects")
@login_required
def portfolio():
    return render_template("portfolio.html", user=current_user)


@views.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        msg = Message(subject=f"Mail from {name}",
                      body=f"Name: {name}\nE-mail: {email}\nSubject:{subject}\n\n {message}", sender=mail_username, recipients=['faith.ifeyemi@gmail.com'])
        mail.send(msg)

        return render_template("contact.html", success=True, user=current_user)

    return render_template("contact.html", user=current_user)


@views.route("/navsearch")
def navsearch():
    return render_template("navsearch.html", user=current_user)


@views.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@views.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    notes = Note.query
    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        # Query the Database
        notes = notes.filter(Note.data.like('%' + post.searched + '%'))
        notes = notes.order_by(Note.date).all()

        return render_template("search.html",
                               form=form,
                               searched=post.searched,
                               notes=notes, user=current_user
                               )


@views.route("/notes", methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("notes.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

        return jsonify({})
