#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# __author__ = 'Benjamin'


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


def update_downloaded():

    for amendement in session.query(tableAmendements).all():
        if not amendement.downloaded_status:
            download_amd(amendement)


if __name__ == "__main__":

    update_downloaded()