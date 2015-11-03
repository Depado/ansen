import os

from flask import render_template, flash, redirect
from app import app
from .forms import LoginForm

from sqlalchemy import Column, Integer, String, create_engine, func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
engine = create_engine('sqlite:///{}'.format(os.path.join(SCRIPT_DIR, 'core', 'AN.db')))
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# Declares object structure included in database
class tableProjets(Base):
    __tablename__ = 'Projets'
    id = Column(Integer, primary_key=True)
    n_dossier = Column(Integer)
    cat_dossier = Column(String)
    nom_dossier = Column(String)
    n_examen = Column(Integer)
    nom_examen = Column(String)
    nb_amd = Column(Integer, default=0)
    last_check = Column(DateTime(timezone=True), default=func.now())
    sqlite_autoincrement = True


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="%s", remember_me=%s' %
              (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html',
                           title='Sign In',
                           form=form)

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Benjamin'}
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("index.html",
                           title='Home',
                           user=user,
                           posts=posts)

@app.route('/sen')
@app.route('/an')
def an():
    user = {'nickname': 'Benjamin'}
    projets = []
    for projet in session.query(tableProjets).all():
        projets.append({ 'name' : projet.nom_dossier, 'nb_amd' : projet.nb_amd})

    return render_template("an_listing.html",
                       title='AN - Liste',
                       user=user,
                       projets = projets)
