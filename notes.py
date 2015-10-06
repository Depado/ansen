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


# Décomposition de la requete JQuery pour lister les examens, adressable avec un simple requests

# http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement
# &idDossierLegislatif=33309
# &idExamen=&idArticle=&idAlinea=&sort=&numAmend=&idAuteur=&typeRes=facettes


# Décomposition de la requete JQuery pour lister les amendements, adressable avec un simple requests

# http://www2.assemblee-nationale.fr/recherche/query_amendements?typeDocument=amendement
# &idExamen=3265
# &idDossierLegislatif=31756
# &numAmend=&idAuteur=&idArticle=&idAlinea=&sort=&dateDebut=&dateFin=&periodeParlementaire=&texteRecherche=&rows=500&format=html&tri=ordreTexteasc
# &start=1&typeRes=liste

# store as dict
# dico['infoGenerales']['texte_concerne']
# dict['infoGenerales']['nb_resultats']
# dict['data_table']

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.types import DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
engine = create_engine('sqlite:///{}'.format(os.path.join(SCRIPT_DIR, 'database.db')))
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Projects(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    cat_dossier = Column(String)
    nom_dossier = Column(String)
    n_examen = Column(Integer)
    nom_examen = Column(String)
    nb_amd = Column(Integer)
    last = Column(DateTime)
    sqlite_autoincrement=True
