#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = 'Benjamin'

from lxml import html
from selenium import webdriver
import sqlite3 as lite
import requests
import time, re

# Format adresse site web
base_url = "http://www2.assemblee-nationale.fr/recherche/amendements"
append_dossier = "#idDossierLegislatif="
append_examen = "&idExamen="
app_end = "&numAmend=&idAuteur=&idArticle=&idAlinea=&sort=&dateDebut=&dateFin=&periodeParlementaire=&texteRecherche=" \
          "&zoneRecherche=tout&nbres=500&format=html&regleTri=ordre_texte&ordreTri=croissant&start=1"

# Récupère la liste des projets ('dossier' ou 'examen')
global browser

def getlist_gen(url, type):
    global browser
    browser.get(url)
    time.sleep(1)
    browser.refresh()
    time.sleep(8)
    tree = html.fromstring(browser.page_source)
    return tree.xpath(str('//*[@id="field_' + type + 'Composite"]/option/@value')),\
           tree.xpath(str('//*[@id="field_' + type + 'Composite"]/option/text()'))

def update_db_proj(db):
    global browser
    browser = webdriver.Firefox()
    list_dossier_id, list_dossier_name = getlist_gen(base_url, 'dossier')
    list_dossier_id.pop(0)
    list_dossier_name.pop(0)
    database = lite.connect(db)
    c = database.cursor()
    c.execute('''DROP TABLE IF EXISTS projets''')
    c.execute('''CREATE TABLE projets (n_dossier INT, cat_dossier TEXT, nom_dossier TEXT, n_examen INT, nom_examen TEXT, nb_amd INT, last_check TEXT)''')

    for i, dossier in enumerate(list_dossier_id):
        temp_str = str(list_dossier_name[i]).translate({ord(c): " " for c in "\'\""}) # Removes .'. chars from string
        p = re.compile('([A-Za-zéàèîïôêçû \’\-\,]*)([\: ]*)([ \(a-zA-Zéàèîïôêçû0-9\’\-\:\,\°\)]*)')
        if re.search(p,temp_str).group(2) != "":
            categorie = re.search(p,temp_str).group(1)
            projet = re.search(p,temp_str).group(3)
        else:
            categorie = " "
            projet = temp_str

        projet_url = base_url + append_dossier + dossier + append_examen + app_end
        list_examen_id, list_examen_name = getlist_gen(projet_url, 'examen')
        list_examen_id.pop(0)

        for j, examen in enumerate(list_examen_id):
            cmd = "INSERT INTO projets VALUES(" + str(list_dossier_id[i]) + ",'" + categorie + "','" + projet + "'," \
                  + list_examen_id[j] + ",'" + list_examen_name[j] + "',0,'" + time.strftime("%Y/%m/%d/-%H:%M") + "')"
            c.execute(cmd)

    database.commit()
    browser.close()
    database.close()

def update_db_amd(db):

    nb = 0
    database = lite.connect(db)
    c = database.cursor()
    c.execute("SELECT * from projets")
    rows = c.fetchall()

    for row in rows:
        query_URL = 'http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement&idExamen=' \
                    + str(row[3]) + '&idDossierLegislatif=' + str(row[0]) + '&numAmend=&idAuteur=&idArticle=&idAlinea=&sort=' \
                                                                            '&dateDebut=&dateFin=&periodeParlementaire=' \
                                                                            '&texteRecherche=&rows=500&format=html' \
                                                                            '&tri=ordreTexteasc&start=1&typeRes=liste'
        try:
            response = requests.get(query_URL)
            data = response.json()
        except:
            data ={"infoGenerales" : {"nb_resultats" : 0}}

        cmd = "UPDATE projets SET nb_amd=" + str(data['infoGenerales']['nb_resultats']) + " WHERE n_examen= " +  str(row[3])
        c.execute(cmd)
        nb = nb + data['infoGenerales']['nb_resultats']

    database.commit()
    print(nb)
    database.close()


