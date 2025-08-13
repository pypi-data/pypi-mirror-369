import os
import time

def wait_for_file(path, filename, retry=20):
    """
    Attends qu'un fichier spécifique soit disponible dans un répertoire donné, avec un nombre limité de tentatives.
    :param path: Le chemin du répertoire où chercher le fichier.
    :param filename: Le nom du fichier à attendre dans le répertoire spécifié.
    :param retry: Le nombre maximal de tentatives pour vérifier la présence du fichier (par défaut 20).
    :raises ValueError: Si le chemin spécifié dans `path` n'existe pas.
    :return: Retourne True si le fichier est trouvé dans le nombre de tentatives, sinon False.
    """
    i=1
    res = False
    if not os.path.exists(path):
        raise "Error : path does not exist"
    while not os.path.isfile(os.path.join(path, filename)) and i <= retry:
        time.sleep(1)
        i += 1
    if i <= retry:
        res = True
    return res
