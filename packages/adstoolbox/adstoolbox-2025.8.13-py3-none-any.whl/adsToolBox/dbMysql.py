import os
import mysql.connector
import timeit
import polars as pl

from .timer import timer, get_timer
from .dataFactory import data_factory

class dbMysql(data_factory):
    def __init__(self, dictionnary: dict, logger, batch_size=10_000):
        """
        instancie la classe dbMysql, qui hérite de dataFactory
        :param dictionnary: Un dictionnaire contenant tous les paramètres nécéssaires pour lancer une connexion MySQL
        :param logger: Un logger ads qui va gérer les logs des actions de la classe
        :param batch_size: La taille des batchs en lecture et écriture
        """
        self.connection = None
        self.logger = logger
        self.__database = dictionnary.get("database")
        self.__user = dictionnary.get("user")
        self.__password = dictionnary.get("password")
        self.__port = dictionnary.get("port")
        self.__host = dictionnary.get("host")
        self.batch_size = batch_size

    def connect(self, additionnal_parameters=None):
        """
        Lance la connexion avec les identifiants passés à l'initialisation de la classe
        Toutes les méthodes de la classe nécéssitent une connexion active
        :return: La connexion
        """
        if self.logger is not None: self.logger.info("Tentative de connexion avec la base de données.")
        try:
            self.connection = mysql.connector.connect(**{
                'user': self.__user,
                'password': self.__password,
                'host': self.__host,
                'port': self.__port,
                'database': self.__database,
            })
            if additionnal_parameters:
                cursor = self.connection.cursor()
                for param, value in additionnal_parameters.items():
                    cursor.execute(f"SET SESSION {param} = {value}")
                self.connection.commit()
            if self.logger is not None: self.logger.info("Connexion établie avec la base de données.")
            return self.connection
        except Exception as e:
            if self.logger is not None: self.logger.error(f"Échec de la connexion à la base de données: {e}")
            raise

    def sqlQuery(self, query: str, return_columns: bool = False):
        """
        lit la base de données avec la requête query
        :param return_columns: booléen qui indique si l'on veut récupérer les colonnes de la tables
        :param query: la requête
        :return: les données lues avec yield
        """
        self.logger.debug(f"Exécution de la requête de lecture: {query}")
        try:
            timer_start = timeit.default_timer()
            cpt_rows = 0
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                if return_columns:
                    cols = [desc[0] for desc in cursor.description]
                    yield cols
                self.logger.info("Requête exécutée avec succès, début de la lecture des résultats.")
                while True:
                    rows = cursor.fetchmany(self.batch_size)
                    if not rows:
                        break
                    yield rows
                    cpt_rows += len(rows)
                    self.logger.info(f"{cpt_rows} ligne(s) lue(s).")
            if get_timer():
                elapsed_time = timeit.default_timer() - timer_start
                self.logger.info(f"Temps d'exécution de sqlQuery: {elapsed_time:.4f} secondes.")
        except Exception as e:
            self.logger.error(f"Échec de la lecture des données: {e}")
            raise

    @timer
    def sqlExec(self, query):
        """
        Exécute une requête sur la base de données, un create ou delete table par exemple
        :param query: La requête en question
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
                self.logger.info(f"Requête exécutée avec succès.")
        except Exception as e:
            self.logger.error(f"Échec de l'exécution de la requête: {e}")
            raise

    @timer
    def sqlScalaire(self, query):
        """
        Exécute une requête et retourne le premier résultat
        :param query: La requête en question
        :return: Le résultat de cette requête
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                self.logger.info(f"Requête scalaire exécutée avec succès.")
                return result[0] if result else None
        except Exception as e:
            self.logger.error(f"Échec de l'exécution de la requête: {e}")
            raise

    @timer
    def insert(self, schema: str, table: str, cols: [], row: []):
        """
        Insère une ligne de données dans la base de données
        :param table: Nom de la table dans laquelle insérer
        :param cols: Liste des colonnes dans lesquelles insérer
        :param row: Liste des valeurs à insérer
        :return: Le résultat de l'opération
        """
        placeholders = ', '.join(["%s"] * len(cols))
        table = f"{schema}.{table}" if schema else table
        query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, row)
                self.connection.commit()
                self.logger.info(f"{len(row)} valeurs insérées avec succès dans la table {table}")
                return "SUCCESS", [], []
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Échec de l'insertion des données: {e}")
            return "ERROR", str(e), row

    @timer
    def insertMany(self, schema: str, table: str, cols: [], rows: [[]]):
        """
        Insère des données par batch dans une table avec gestion des erreurs

        :param schema: Nom du schéma dans lequel se trouve la table
        :param table: Nom de la table dans laquelle insérer
        :param cols: Liste des colonnes dans lesquelles insérer
        :param rows: Liste des lignes à insérer
        :return: Le résultat de l'opération, l'erreur et la le batch concerné en cas d'erreur
        """
        failed_batches = []
        errors = []
        total_inserted = 0
        placeholders = ', '.join(["%s"] * len(cols))
        table = f"{schema}.{table}" if schema else table
        query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
        try:
            with self.connection.cursor() as cursor:
                for batch_index, start in enumerate(range(0, len(rows), self.batch_size), start=1):
                    batch = rows[start: start + self.batch_size]
                    try:
                        cursor.executemany(query, batch)
                        self.connection.commit()
                        total_inserted += len(batch)
                        self.logger.info(
                            f"Batch {batch_index}: {len(batch)} ligne(s) insérée(s) avec succès dans la table {table}. "
                            f"Total inséré: {total_inserted}/{len(rows)} ligne(s)."
                        )
                    except Exception as batch_error:
                        self.connection.rollback()
                        self.logger.error(f"Erreur lors de l'insertion du batch {batch_index}: {batch_error}")
                        failed_batches.append(batch)
                        errors.append(str(batch_error))
                return ("ERROR" if failed_batches else "SUCCESS"), errors, failed_batches
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Erreur critique lors de l'insertion des données: {e}")
            return "ERROR", str(e), rows

    def __get_df(self, rows, cols):
        if isinstance(rows, list):
            df = pl.DataFrame(rows, schema=cols, orient='row', infer_schema_length=len(rows))
        elif isinstance(rows, pl.DataFrame):
            df = rows
        else:
            raise ValueError("Les données doivent être une liste de tuples ou un DataFrame polars")
        return df

    @timer
    def insertBulk(self, schema: str, table: str, cols: [], rows):
        """
        Insère des données dans une table en bulk, en lots

        :param schema: Nom du schéma
        :param table: Nom de la table dans laquelle insérer
        :param cols: Liste des colonnes dans lesquelles insérer
        :param rows: Liste des lignes à insérer
        :return: Le résultat de l'opération, l'erreur et la le batch concerné en cas d'erreur
        """
        failed_batches = []
        errors = []
        total_inserted = 0
        table_full = f"{schema}.{table}" if schema else table
        temp_file = "temp_bulk_insert.csv"
        query = f"""
        LOAD DATA LOCAL INFILE '{temp_file}'
        INTO TABLE {table_full}
        FIELDS TERMINATED BY ','
        LINES TERMINATED BY '\n'
        ({', '.join(cols)})
        """
        try:
            df = self.__get_df(rows, cols)
            n_rows = df.shape[0]
            with self.connection.cursor() as cursor:
                for batch_index, start in enumerate(range(0, n_rows, self.batch_size), start=1):
                    batch = df.slice(start, self.batch_size)
                    try:
                        batch.write_csv(temp_file, include_header=False)
                        cursor.execute(query)
                        self.connection.commit()
                        os.remove(temp_file)
                        total_inserted += batch.shape[0]
                        self.logger.info(f"Batch {batch_index}: {batch.shape[0]} ligne(s) insérée(s) avec succès dans la table {table_full}. "
                                         f"Total inséré: {total_inserted}/{n_rows} ligne(s).")
                    except Exception as batch_error:
                        self.connection.rollback()
                        self.logger.error(f"Erreur lors de l'insertion du batch {batch_index}: {batch_error}")
                        failed_batches.append(batch)
                        errors.append(str(batch_error))
            return ("ERROR" if failed_batches else "SUCCESS"), errors, failed_batches
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Erreur critique lors de l'insertion des données: {e}")
            return "ERROR", str(e), rows
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    @timer
    def upsert(self, schema: str, table: str, cols: [], row: [], conflict_cols: []):
        """
        Réalise une opération upsert sur la base
        :param schema: Le schéma de la table
        :param table: Le nom de la table
        :param cols: Liste des colonnes dans lequelles insérer
        :param row: Liste des valeurs à insérer
        :param conflict_cols: Colonnes à utiliser pour détecter les conflits
        :return: Le résultat de l'opération, l'erreur et la ligne en cas d'erreur
        """
        table_full = f"{schema}.{table}" if schema else table
        columns = ', '.join([f"'{col}'" for col in cols])
        placeholders = ', '.join(['%s'] * len(cols))
        update_clause = ', '.join([f"'{col}' = VALUES('{col}')" for col in cols if col not in conflict_cols])
        query = f"""
        INSERT INTO {table_full} ({columns})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause};
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, row)
                self.connection.commit()
                self.logger.info(f"{len(row)} valeurs insérée(s) ou mise(s) à jour dans la table {table_full}.")
                return "SUCCESS", [], []
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Erreur lors de l'upsert dans la table {table}.")
            return "ERROR", str(e), row

    @timer
    def upsertMany(self, schema: str, table: str, cols: [], rows: [[]], conflict_cols: []):
        """
        Réalise une opération upsert par batch sur la base
        :param schema: Le schéma de la table
        :param table: Le nom de la table
        :param cols: Liste des colonnes dans lequelles insérer
        :param rows: Liste des lignes à insérer
        :param conflict_cols: Colonnes à utiliser pour détecter les conflits
        :return: Le résultat de l'opération, l'erreur et le batch en cas d'erreur
        """
        failed_batches = []
        errors = []
        total_inserted = 0
        table_full = f"{schema}.{table}" if schema else table
        columns = ', '.join([f"'{col}'" for col in cols])
        placeholders = ', '.join(['%s'] * len(cols))
        update_clause = ', '.join([f"'{col}' = VALUES('{col}')" for col in cols if col not in conflict_cols])
        query = f"""
        INSERT INTO {table_full} ({columns})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause};
        """
        try:
            with self.connection.cursor() as cursor:
                for batch_index, start in enumerate(range(0, len(rows), self.batch_size), start=1):
                    batch = rows[start: start + self.batch_size]
                    try:
                        cursor.executemany(query, batch)
                        self.connection.commit()
                        total_inserted += len(batch)
                        self.logger.info(
                            f"Batch {batch_index}: {len(batch)} ligne(s) insérée(s) ou mise(s) à jour dans la table {table}. "
                            f"Total inséré ou mis à jour: {total_inserted}/{len(rows)} ligne(s)."
                        )
                    except Exception as batch_error:
                        self.connection.rollback()
                        self.logger.error(f"Erreur lors de l'upsert du batch {batch_index}: {batch_error}")
                        failed_batches.append(batch)
                        errors.append(str(batch_error))
            return ("ERROR" if failed_batches else "SUCCESS"), errors, failed_batches
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Erreur critique lors de l'upsert des données: {e}")
            return "ERROR", str(e), rows

    @timer
    def upsertBulk(self, schema: str, table: str, cols: [], rows, conflict_cols: []):
        """
        Réalise une opération upsert par batch sur la base avec LOAD DATA INFILE et une table temporaire.

        :param schema: Le schéma de la table
        :param table: Le nom de la table
        :param cols: Liste des colonnes dans lesquelles insérer
        :param rows: Liste des lignes à insérer
        :param conflict_cols: Colonnes à utiliser pour détecter les conflits
        :return: Le résultat de l'opération, les erreurs et les lots échoués
        """
        temp_table = f"{table}_temp"
        table_full, temp_table_full = (f"{schema}.{table}", f"{schema}.{temp_table}") if schema else (table, temp_table)
        columns = ', '.join(cols)
        update_clause = ', '.join([f"{col} = VALUES({col})" for col in cols if col not in conflict_cols])
        query = f"""
        INSERT INTO {table_full} ({columns})
        SELECT {columns} FROM {temp_table_full}
        ON DUPLICATE KEY UPDATE {update_clause};
        """
        try:
            self.sqlExec(f"CREATE TEMPORARY TABLE {temp_table_full} LIKE {table_full}")
            self.logger.info(f"Table temporaire {temp_table_full} créée.")
            result, errors, failed_batches = self.insertBulk(schema, temp_table, cols, rows)
            if result == "ERROR":
                return result, errors, failed_batches
            self.sqlExec(query)
            self.logger.info(f"{len(rows)} lignes insérée(s) ou mise(s) à jour dans la table {table}.")
            return "SUCCESS", [], []
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Erreur critique lors de l'UPSERT : {e}")
            return "ERROR", str(e), rows
        finally:
            self.sqlExec(f"DROP TEMPORARY TABLE IF EXISTS {temp_table_full}")
            self.logger.info(f"Table temporaire {temp_table_full} supprimée.")
