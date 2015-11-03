#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# __author__ = 'Benjamin'

import os, sys, re, math
import requests
import time, timeit
from lxml import html
from math import ceil

from sqlalchemy import Column, Boolean, Integer, String, create_engine, func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# SQLAlchemy session and db opening
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
engine = create_engine('sqlite:///{}'.format(os.path.join(SCRIPT_DIR, 'AN.db')))
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


class tableAmendements(Base):
    __tablename__ = 'Amendements'
    id = Column(Integer, primary_key=True)
    n_dossier = Column(Integer)
    n_examen = Column(Integer)
    n_amendement = Column(Integer)
    url_amendement = Column(String)
    downloaded_status = Column(Boolean, default=False)
    date_created = Column(DateTime(timezone=True), default=func.now())
    sqlite_autoincrement = True


def get_or_create(session, model, **kwargs):

    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance, True


def download_pdf(source, target):
    try:
        r = requests.get(source, stream=True)
        if r.status_code == 200:
            with open(target, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        return True
    except:
        return False


def get_projectlist(url, type_ed):  # Get project list as 'dossier' or 'examen'

    page = requests.get(url)
    tree = html.fromstring(page.text)
    return tree.xpath(str('//*[@id="field_' + type_ed + 'Composite"]/option/@value')),\
           tree.xpath(str('//*[@id="field_' + type_ed + 'Composite"]/option/text()'))


def update_projets_list():

    base_url = "http://www2.assemblee-nationale.fr/recherche/amendements"
    list_dossier_id, list_dossier_name = get_projectlist(base_url, 'dossier')
    list_dossier_id.pop(0)
    list_dossier_name.pop(0)

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
        except:
            data['examenComposite'] = [{'txt': 'NULL', 'val': '0000'}]

        for exam_t in data['examenComposite']:
            list_examen_name.append(exam_t['txt'])
            list_examen_id.append(exam_t['val'])

        for j, examen in enumerate(list_examen_id):
            get_or_create(session, tableProjets, n_dossier=list_dossier_id[i], cat_dossier=categorie,
                                     nom_dossier=projet, n_examen=list_examen_id[j], nom_examen=list_examen_name[j])


def update_amd():

    for projet in session.query(tableProjets).all():
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
            update_amd_list(projet)

        projet.last_check = func.now()
        session.commit()


def update_amd_list(projet):

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
            data['data_table'] = ['|||||||||||',]  # Website can provide bad formating response to request

        for j, amd in enumerate(data['data_table']):
            temp_list = data['data_table'][j].split('|')
            temp_amd, created = get_or_create(session, tableAmendements, n_dossier=projet.n_dossier,
                                    n_examen=projet.n_examen, n_amendement=temp_list[5], url_amendement=temp_list[6])
            if not temp_amd.downloaded_status:
                download_amd(temp_amd)
        session.commit()


def update_downloaded():

    for amendement in session.query(tableAmendements).all():
        if not amendement.downloaded_status:
            download_amd(amendement)


def download_amd(amendement):

    raw_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(raw_path+'/storage'):
        os.mkdir(raw_path+'/storage', mode=0o777)

    amd_path = "storage/" + str(amendement.n_dossier) +"/" + str(amendement.n_examen)
    if not os.path.exists(raw_path+ '/' + amd_path):
        os.makedirs(raw_path + '/' + amd_path, mode=0o777)

    url_source = amendement.url_amendement[:-3] + 'pdf'
    file_name = url_source.split("/")[-1]
    target_file = raw_path + "/"+ amd_path +"/" + file_name

    amendement.downloaded_status = download_pdf(url_source, target_file)
    if amendement.downloaded_status:
        amendement.date_created = func.now()

def orga_db_update(arg):

    if arg == 'AN':
        # Retry to download last failed
        update_downloaded()

        # Update list of projects
        update_projets_list()

        # Update amd list and download new ones
        update_amd()


if __name__ == "__main__":
    start = timeit.default_timer()

    # Creates Bases if not exist
    Base.metadata.create_all(engine)

    attributes = sys.argv[1:]   # attribute should be 'AN', 'SN' of both
    if len(attributes) > 2 :
        os.stderr.write('Too much parameter')

    for organisme in attributes:
        try:
            if organisme == ('AN' or 'SN'):
                orga_db_update(organisme)
            else:
                os.stderr.write('Unknown parameter')
        except:
            os.stderr.write('Not enough parameter')

    stop = timeit.default_timer()
    session.close()

    with open(os.path.dirname(os.path.realpath(__file__)) +'/output.log','a') as log:
        log.write('\n' + time.strftime("%Y/%m/%d - %H:%M") + ' | ' + str(ceil(stop - start)) + ' seconds')