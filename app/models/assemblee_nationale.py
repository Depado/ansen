# -*- coding: utf-8 -*-

from app import db
from sqlalchemy.sql import func


class DossierAN(db.Model):
    __tablename__ = "dossier_an"
    id = db.Column(db.Integer, primary_key=True)
    projets = db.relationship('Projets', backref=db.backref('projet_an.id', lazy='dynamic'))

    numero = db.Column(db.Integer)
    categorie = db.Column(db.String)
    nom = db.Column(db.String)


class ExamenAN(db.Model):
    __tablename__ = "examen_an"
    id = db.Column(db.Integer, primary_key=True)
    projets = db.relationship('Projets', backref=db.backref('projet_an.id', lazy='dynamic'))

    numero = db.Column(db.Integer)
    nom = db.Column(db.String)


class ProjetAN(db.Model):
    __tablename__ = 'projet_an'
    id = db.Column(db.Integer, primary_key=True)
    dossier_id = db.Column(db.Integer, db.ForeignKey('dossier_an.id'))
    examen_id = db.Column(db.Integer, db.ForeignKey('examen_an.id'))

    nb_amd = db.Column('nb_amd', db.Integer, default=0)
    last_check = db.Column(db.DateTime(timezone=True), default=func.now())


class AmendementAN(db.Model):
    __tablename__ = 'amendement_an'
    id = db.Column(db.Integer, primary_key=True)
    dossier_id = db.Column(db.Integer, db.ForeignKey('dossier_an.id'))
    examen_id = db.Column(db.Integer, db.ForeignKey('examen_an.id'))

    numero = db.Column(db.Integer)
    url = db.Column(db.String)
    n_article = db.Column(db.Integer)
    downloaded = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    special_type = db.Column(db.String, nullable=True)   # Rédactionnel / Irrecevable / Retiré
