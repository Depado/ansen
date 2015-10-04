#!/usr/bin/python
# -*- coding: UTF-8 -*-
# __author__ = 'Benjamin'

from lxml import html
import sqlite3 as lite
import requests
import time
import math
import re
import os
# import sqlalchemy  # Pass to ORM command


def getlist(url, type_ed):  # Get project list as 'dossier' or 'examen'
    page = requests.get(url)
    tree = html.fromstring(page.text)
    return tree.xpath(str('//*[@id="field_' + type_ed + 'Composite"]/option/@value')),\
           tree.xpath(str('//*[@id="field_' + type_ed + 'Composite"]/option/text()'))


def update_db_proj(db):
    base_url = "http://www2.assemblee-nationale.fr/recherche/amendements"
    list_dossier_id, list_dossier_name = getlist(base_url, 'dossier')
    list_dossier_id.pop(0)
    list_dossier_name.pop(0)
    database = lite.connect(db)
    c = database.cursor()
    c.execute('''DROP TABLE IF EXISTS projets''')
    c.execute('''CREATE TABLE projets (n_dossier INT, cat_dossier TEXT, nom_dossier TEXT, n_examen INT,'''
              '''nom_examen TEXT, nb_amd INT, last_check TEXT)''')

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
                    +'&idExamen=&idArticle=&idAlinea=&sort=&numAmend=&idAuteur=&typeRes=facettes'
        try:
            response = requests.get(query_url)
            data = response.json()
        except:
            data['examenComposite']=[{'txt': 'NULL', 'val': '0000'}]

        for exam_t in data['examenComposite']:
            list_examen_name.append(exam_t['txt'])
            list_examen_id.append(exam_t['val'])

        for j, examen in enumerate(list_examen_id):
            cmd = "INSERT INTO projets VALUES(" + str(list_dossier_id[i]) + ",'" + categorie + "','" + projet + "'," \
                  + list_examen_id[j] + ",'" + list_examen_name[j] + "',0,'" + time.strftime("%Y/%m/%d/-%H:%M") + "')"
            c.execute(cmd)

        database.commit()

    database.close()


def update_db_amd_list(db):
    database = lite.connect(db)
    c = database.cursor()
    c.execute("SELECT * from projets")
    rows = c.fetchall()

    d = database.cursor()
    d.execute('''DROP TABLE IF EXISTS amendements''')
    d.execute('''CREATE TABLE amendements (n_dossier INT, n_examen INT, n_amendement TEXT, url TEXT, last_check TEXT)''')

    for row in rows:
        query_url = 'http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement&idExamen=' \
                    + str(row[3]) + '&idDossierLegislatif=' + str(row[0]) + \
                    '&numAmend=&idAuteur=&idArticle=&idAlinea=&sort=&dateDebut=&dateFin=&periodeParlementaire=' + \
                    '&texteRecherche=&rows=500&format=html&tri=ordreTexteasc&start=1&typeRes=liste'
        try:
            response = requests.get(query_url)
            data = response.json()
        except:
            data = {"infoGenerales": {"nb_resultats": 0}}

        cmd = "UPDATE projets SET nb_amd=" + str(data['infoGenerales']['nb_resultats']) + " WHERE n_examen= " + str(row[3])
        c.execute(cmd)

        nb_page = int(math.ceil(data['infoGenerales']['nb_resultats']/500))
        for i in range(nb_page):
            start_result = i * 500 + 1
            query_url = 'http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement&idExamen=' \
                    + str(row[3]) + '&idDossierLegislatif=' + str(row[0]) + \
                    '&numAmend=&idAuteur=&idArticle=&idAlinea=&sort=&dateDebut=&dateFin=&periodeParlementaire=' \
                    '&texteRecherche=&rows=500&format=html&tri=ordreTexteasc&start=' + str(start_result) + '&typeRes=liste'
            try:
                response = requests.get(query_url)
                data = response.json()
            except:
                data['data_table'][0] = ['|||||||||||']  # Website can provide bad formating response to request

            for j, amd in enumerate(data['data_table']):
                temp_list = data['data_table'][j].split('|')
                cmd = "INSERT INTO amendements VALUES(" + str(row[0]) + "," + str(row[3]) + ",'" + temp_list[5] + "','" \
                  + temp_list[6] + "','" + time.strftime("%Y/%m/%d/-%H:%M") + "')"
                d.execute(cmd)

        database.commit()
    database.close()


def download_amd(db):
    raw_path = os.getcwd()
    if not os.path.exists('storage'):
        os.mkdir('storage', mode=0o777)

    database = lite.connect(db)
    c = database.cursor()
    c.execute("SELECT * from amendements")
    rows = c.fetchall()
    for row in rows:
        amd_path = "storage\\" + str(row[0]) +"\\" + str(row[1])
        if not os.path.exists(amd_path):
            os.makedirs(amd_path, mode=0o777)
        url_dl = row[3][:-3] + 'pdf'
        r = requests.get(url_dl, stream=True)
        if r.status_code == 200:
            file_name = url_dl.split("/")[-1]
            with open(raw_path + "\\"+ amd_path +"\\" + file_name, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
