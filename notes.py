__author__ = 'Benjamin'


# url='http://www2.assemblee-nationale.fr/recherche/amendements#listeResultats=tru&idDossierLegislatif=29173&idExamen=65&numAmend=&idAuteur=&idArticle=&idAlinea=&sort=&dateDebut=&dateFin=&periodeParlementaire=&texteRecherche=&zoneRecherche=tout&nbres=500&format=html&regleTri=ordre_texte&ordreTri=croissant&start=1'
# needs a time sleep of 8-10s
# list_article = tree.xpath('//*[@id="dt_resultats"]/tbody/tr/td/a/text()')

base_url = "http://www2.assemblee-nationale.fr/recherche/amendements"
append_dossier = "#idDossierLegislatif="
append_examen = "&idExamen="
app_end = "&numAmend=&idAuteur=&idArticle=&idAlinea=&sort=&dateDebut=&dateFin=&periodeParlementaire=&texteRecherche=&zoneRecherche=tout&nbres=500&format=html&regleTri=ordre_texte&ordreTri=croissant&start=1"

query json:
#  http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement&idExamen=3265&idDossierLegislatif=31756&numAmend=&idAuteur=&idArticle=&idAlinea=&sort=&dateDebut=&dateFin=&periodeParlementaire=&texteRecherche=&rows=500&format=html&tri=ordreTexteasc&start=1&typeRes=liste
http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement&idExamen=3293&idDossierLegislatif=31757&numAmend=&idAuteur=&idArticle=&idAlinea=&sort=&dateDebut=&dateFin=&periodeParlementaire=&texteRecherche=&rows=500&format=html&tri=ordreTexteasc&start=1&typeRes=liste

# Décomposition de la requete JQuery, adressable avec un simple requests

# http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement
# &idExamen=3265
# &idDossierLegislatif=31756
# &numAmend=&idAuteur=&idArticle=&idAlinea=&sort=&dateDebut=&dateFin=&periodeParlementaire=&texteRecherche=&rows=500&format=html&tri=ordreTexteasc
# &start=1&typeRes=liste

# store as dict
# dico['infoGenerales']['texte_concerne']
# dict['infoGenerales']['nb_resultats']
# dict['data_table']
