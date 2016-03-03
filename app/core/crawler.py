#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# __author__ = 'Benjamin'

import math
import re
import requests
import timeit
from logger import log_info
from lxml import html

from sqlalchemy import Column, Boolean, Integer, String, create_engine, func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy session and DB opening

address_port = 'blawesom.com:6666'  # TBD
engine = create_engine('postgresql://{}'.format(address_port))
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# SQL Class and SQL Functions

class TableProjetsAN(Base):
    __tablename__ = 'Projets_AN'
    id = Column(Integer, primary_key=True)
    n_dossier = Column('n_dossier', Integer)
    cat_dossier = Column('cat_dossier', String)
    nom_dossier = Column('nom_dossier', String)
    n_examen = Column('n_examen', Integer)
    nom_examen = Column('nom_examen', String)
    nb_amd = Column('nb_amd', Integer, default=0)
    last_check = Column('last_check', DateTime(timezone=True), default=func.now())


class TableAmendementsAN(Base):
    __tablename__ = 'Amendements_AN'
    id = Column(Integer, primary_key=True)
    n_dossier = Column('n_dossier', Integer)
    n_examen = Column('n_examen', Integer)
    n_amendement = Column('n_amendement', Integer)
    url_amendement = Column('url_amendement', String)
    n_article = Column('n_article', Integer)
    downloaded_status = Column('downloaded_status', Boolean, default=False)
    date_created = Column('date_created', DateTime(timezone=True), default=func.now())
    special_type = Column('special_type', String, nullable=True)   # Rédactionnel / Irrecevable / Retiré


class TableProjetsSEN(Base):
    __tablename__ = 'Projets_SEN'
    id = Column(Integer, primary_key=True)


class TableAmendementsSEN(Base):
    __tablename__ = 'Amendements_SEN'
    id = Column(Integer, primary_key=True)


def get_or_create(session, model, **kwargs):

    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance, True


# Crawling and Query functions

def get_project_list_an(url, type_ed='dossier'):

    page = requests.get(url)
    hmtl_tree = html.fromstring(page.text)
    list_dossier_id = hmtl_tree.xpath(str('//*[@id="field_' + type_ed + 'Composite"]/option/@value'))
    list_dossier_name = hmtl_tree.xpath(str('//*[@id="field_' + type_ed + 'Composite"]/option/text()'))

    return list_dossier_id[1:], list_dossier_name[1:]


def update_project_list_an():

    base_url = "http://www2.assemblee-nationale.fr/recherche/amendements"
    list_dossier_id, list_dossier_name = get_project_list_an(url=base_url)

    for i, dossier in enumerate(list_dossier_id):
        temp_str = str(list_dossier_name[i]).translate({ord(c): " " for c in "\'\""})  # Removes .'. chars from string
        p = re.compile('([A-Za-zéàèîïôêçû ’\-,]*)([: ]*)([ \(a-zA-Zéàèîïôêçû0-9’\-:,°\)]*)')

        if re.search(p, temp_str).group(2) != "":
            categorie = re.search(p, temp_str).group(1)
            projet = re.search(p, temp_str).group(3)
        else:
            categorie = " "
            projet = temp_str

        list_examen_id = []
        list_examen_name = []
        query_url = 'http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement'\
                    + '&idDossierLegislatif=' + dossier \
                    + '&idExamen=&idArticle=&idAlinea=&sort=&numAmend=&idAuteur=&typeRes=facettes'
        try:
            response = requests.get(query_url)
            data = response.json()
            for exam_t in data['examenComposite']:
                list_examen_name.append(exam_t['txt'])
                list_examen_id.append(exam_t['val'])

            for j, examen in enumerate(list_examen_id):
                get_or_create(session, TableProjetsAN, n_dossier=list_dossier_id[i], cat_dossier=categorie,
                                         nom_dossier=projet, n_examen=list_examen_id[j], nom_examen=list_examen_name[j])
        except:
            log_info('Erreur sur le dossier n {}'.format(dossier))


def update_amd_list_an(projet):

    nb_page = int(math.ceil(projet.nb_amd/500))
    for i in range(nb_page):
        start_result = i * 500 + 1
        query_url = 'http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement&idExamen=' \
                + str(projet.n_examen) + '&idDossierLegislatif=' + str(projet.n_dossier) + \
                '&numAmend=&idAuteur=&idArticle=&idAlinea=&sort=&dateDebut=&dateFin=&periodeParlementaire=' \
                '&texteRecherche=&rows=500&format=html&tri=ordreTexteasc&start=' + str(start_result) + '&typeRes=liste'
        try:
            response = requests.get(query_url)
            data = response.json()
        except:
            data = {}
            data['data_table'] = ['|||||||||||', ]  # Website can provide bad formating response to request

        for j, amd in enumerate(data['data_table']):
            temp_list = data['data_table'][j].split('|')
            temp_amd, created = get_or_create(session, TableAmendementsAN, n_dossier=projet.n_dossier,
                                    n_examen=projet.n_examen, n_amendement=temp_list[5], url_amendement=temp_list[6])
        session.commit()


def update_amd_an():

    for projet in session.query(TableProjetsAN).all():
        query_url = 'http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement&idExamen=' \
                    + str(projet.n_examen) + '&idDossierLegislatif=' + str(projet.n_dossier) + \
                    '&missionVisee=&numAmend=&idAuteur=&idArticle=&idAlinea=&sort=&dateDebut=&dateFin=&periodeParlementaire=' + \
                    '&texteRecherche=&rows=500&format=html&tri=ordreTexteasc&start=1&typeRes=liste'
        try:
            response = requests.get(query_url)
            data = response.json()
            nb = data['infoGenerales']['nb_resultats']
        except:
            nb = 0  # in case of bad format provided

        if nb != projet.nb_amd:
            projet.nb_amd = nb
            update_amd_list_an(projet)

        projet.last_check = func.now()
        session.commit()


def orga_db_update(arg):

    if arg == 'AN':
        # Update list of projects
        update_project_list_an()

        # Update amd list and download new ones
        update_amd_an()
    else:
        os.stderr.write('Function not implemented')


if __name__ == "__main__":

    # Creates Bases if not exist
    Base.metadata.create_all(engine)

    attributes = sys.argv[1:]   # attribute should be 'AN', 'SEN' of both
    if len(attributes) > 2 :
        os.stderr.write('Too much parameter')

    for organisme in attributes:
        try:
            if organisme == ('AN' or 'SEN'):
                orga_db_update(organisme)
            else:
                os.stderr.write('Unknown parameter')
        except:
            os.stderr.write('Not enough parameter')

    session.close()