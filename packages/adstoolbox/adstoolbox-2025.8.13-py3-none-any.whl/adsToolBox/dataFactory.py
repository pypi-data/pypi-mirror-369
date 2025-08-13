from abc import ABC, abstractmethod

class data_factory(ABC):
    """
    classe abstraite qui pose un modèle de connexion ads
    """
    @abstractmethod
    def connect(self):
        """
        lance la connexion avec les identifiants passés à l'initialisation de la classe
        :return: la connexion
        """
        pass

    @abstractmethod
    def insert(self,table,cols=[],rows=[]):
        """
        insère des données dans la base de données, nécessite une connexion active
        :param table: nom de la table dans laquelle insérer
        :param cols: liste des colonnes dans lesquelles insérer
        :param rows: liste des valeurs à insérer
        """
        pass

    @abstractmethod
    def insertBulk(self,table,cols=[],rows=[]):
        """
        similaire à insert classique, mais insère par batch de taille 'batch_size' définie
        :param table: nom de la table dans laquelle insérer
        :param cols: liste des colonnes dans lesquelles insérer
        :param rows: liste des lignes à insérer
        """
        pass

    @abstractmethod
    def sqlQuery(self,query):
        """
        lit la base de données avec la requête query
        :param query: la requête
        :return: les données lues
        """
        pass

    @abstractmethod
    def sqlExec(self, query: str, params=None):
        """
        execute une requête sur la base de données
        :param query: la requête
        :param params: d'éventuels paramètres à ajouter si la requête contient des variables
        """
        pass