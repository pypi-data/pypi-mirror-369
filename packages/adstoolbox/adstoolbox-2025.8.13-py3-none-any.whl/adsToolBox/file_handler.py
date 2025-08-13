import os
import timeit
import unicodedata
import smbclient
import chardet
from .timer import timer, get_timer

class FileHandler:
    def __init__(self, logger, smb_config: dict=None, batch_size: int=4_096):
        """
        Initialise le gestionnaire de fichiers avec le chemin du fichier
        """
        self.logger = logger
        self.smb_config = smb_config
        self.batch_size = batch_size
        if smb_config:
            self._setup_smb_connection()

    @timer
    def _setup_smb_connection(self):
        """
        Configure la connection SMB
        """
        try:
            smbclient.register_session(
                self.smb_config.get("server"),
                username=self.smb_config.get("username"),
                password=self.smb_config.get("password")
            )
            self.logger.info("Connexion SMB établie.")
        except Exception as e:
            self.logger.error(f"Échec de la connexion SMB : {e}")
            raise

    def read_file(self, file_path: str, mode: str='rb', encoding: str=None):
        """
        Lit un fichier local ou SMB en batchs
        """
        if self.smb_config and file_path.startswith("//"):
            return self._read_smb_file(file_path, mode, encoding)
        return self._read_local_file(file_path, mode, encoding)

    def _read_smb_file(self, file_path, mode, encoding):
        """
        Lit un fichier sur un partage SMB en batchs
        """
        timer_start = timeit.default_timer()
        try:
            with smbclient.open_file(file_path, mode=mode, encoding=encoding) as file:
                while chunk := file.read(self.batch_size):
                    yield chunk
                self.logger.info(f"Lecture réussie du fichier : {file_path}")
            if get_timer():
                elapsed_time = timeit.default_timer() - timer_start
                self.logger.info(f"Temps d'exécution de sqlQuery: {elapsed_time:.4f} secondes")
        except Exception as e:
            self.logger.error(f"Erreur de lecture du fichier SMB : {e}")
            raise

    def _read_local_file(self, file_path, mode, encoding):
        """
        Lit un fichier en local en batchs
        """
        timer_start = timeit.default_timer()
        try:
            with open(file_path, mode=mode, encoding=encoding) as file:
                while chunk := file.read(self.batch_size):
                    yield chunk
                self.logger.info(f"Lecture réussie du fichier: {file_path}")
            if get_timer():
                elapsed_time = timeit.default_timer() - timer_start
                self.logger.info(f"Temps d'exécution de sqlQuery: {elapsed_time:.4f} secondes")
        except Exception as e:
            self.logger.error(f"Erreur de lecture du fichier en local: {e}")
            raise

    @timer
    def write_file(self, file_path: str, content, mode: str='wb', clean: bool=False):
        """
        Écrit du contenu dans un fichier local ou SMB en batchs
        """
        if clean:
            self.logger.info(f"Nettoyage du fichier {file_path}.")
        if self.smb_config and file_path.startswith("//"):
            return self._write_smb_file(file_path, content, mode, clean)
        return self._write_local_file(file_path, content, mode, clean)

    def _write_smb_file(self, file_path, content, mode, clean: bool=False):
        """
        Écrit du contenu dans un fichier via partage SMB en batchs
        """
        try:
            encoding = "utf-8" if "b" not in mode else None
            with smbclient.open_file(file_path, mode=mode, encoding=encoding) as file:
                for chunk in content:
                    if clean:
                        chunk = self.clean_text(chunk)
                    for i in range(0, len(chunk), self.batch_size):
                        file.write(chunk[i:i + self.batch_size])
                self.logger.info(f"Succès : contenu écrit dans '{file_path}' (SMB).")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'écriture du fichier '{file_path}' via SMB: {e}")
            raise

    def _write_local_file(self, file_path, content, mode, clean: bool=False):
        """
        Écrit du contenu dans un fichier local en batchs
        """
        try:
            encoding = "utf-8-sig" if "b" not in mode else None
            with open(file_path, mode=mode, encoding=encoding) as file:
                for chunk in content:
                    if clean:
                        chunk = self.clean_text(chunk)
                    for i in range(0, len(chunk), self.batch_size):
                        file.write(chunk[i:i + self.batch_size])
                self.logger.info(f"Succès: Contenu écrit dans '{file_path}' (local).")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'écriture du fichier '{file_path}' en local: {e}")
            raise

    def list_dir(self, dir_path: str):
        """
        Liste le contenu d'un dossier en local ou via SMB
        """
        try:
            if self.smb_config and dir_path.startswith("//"):
                return smbclient.listdir(dir_path)
            return os.listdir(dir_path)
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture du dossier {dir_path}: {e}")
            return []

    def file_exists(self, file_path: str):
        """
        Vérifie si le fichier existe (local ou SMB)
        """
        if self.smb_config and file_path.startswith("//"):
            return self._smb_file_exists(file_path)
        return self._local_file_exists(file_path)

    def _smb_file_exists(self, file_path):
        """
        Vérifie si un fichier SMB existe
        """
        try:
            exists = smbclient.path.exists(file_path) and smbclient.path.isfile(file_path)
            if exists:
                self.logger.info(f"Le fichier existe: {file_path}")
            else:
                self.logger.warning(f"Le fichier n'existe pas: {file_path}")
            return exists
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification d'existence du fichier SMB: {e}")

    def _local_file_exists(self, file_path):
        """
        Vérifie si un fichier en local existe
        """
        exists = os.path.exists(file_path) and os.path.isfile(file_path)
        if exists:
            self.logger.info(f"Le fichier existe: {file_path}")
        else:
            self.logger.warning(f"Le fichier n'existe pas: {file_path}")
        return exists

    def directory_exists(self, dir_path: str):
        """
        Vérifie si le fichier existe (local ou SMB)
        """
        if self.smb_config and dir_path.startswith("//"):
            return self._smb_directory_exists(dir_path)
        return self._local_directory_exists(dir_path)

    def _smb_directory_exists(self, dir_path: str):
        try:
            exists = smbclient.path.exists(dir_path) and smbclient.path.isdir(dir_path)
            if exists:
                self.logger.info(f"Le dossier existe: {dir_path}")
            else:
                self.logger.warning(f"Le dossier n'existe pas: {dir_path}")
            return exists
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification du dossier SMB: {e}")

    def _local_directory_exists(self, dir_path):
        exists = os.path.exists(dir_path) and os.path.isdir(dir_path)
        if exists:
            self.logger.info(f"Le dossier existe: {dir_path}")
        else:
            self.logger.warning(f"Le dossier n'existe pas: {dir_path}")
        return exists

    def remove_file(self, file_path: str):
        """
        Supprime un fichier (local ou SMB)
        """
        try:
            if self.smb_config and file_path.startswith("//"):
                smbclient.remove(file_path)
            else:
                os.remove(file_path)
            self.logger.info(f"Fichier supprimé avec succès.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression du fichier '{file_path}': {e}")
            raise

    def create_empty_file(self, file_path: str, mode: str='wb'):
        """
        Crée un fichier vide (local ou SMB)
        """
        try:
            if self.smb_config and file_path.startswith("//"):
                with smbclient.open_file(file_path, mode=mode) as file:
                    pass
                self.logger.info(f"Fichier vide créé sur SMB: {file_path}")
            else:
                with open(file_path, mode=mode) as file:
                    pass
                self.logger.info(f"Fichier vide créé localement: {file_path}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du fichier vide '{file_path}': {e}")
            raise

    def clean_text(self, text):
        if isinstance(text, bytes):
            encoding = chardet.detect(text)["encoding"]
            text = text.decode(encoding or "utf-8", errors='ignore')
        text = unicodedata.normalize('NFKD', text)
        text = ''.join([c for c in text if not unicodedata.combining(c)])
        text = ''.join([f'&#{ord(c)};' if ord(c) > 127 else c for c in text])
        return text.encode("utf-8")