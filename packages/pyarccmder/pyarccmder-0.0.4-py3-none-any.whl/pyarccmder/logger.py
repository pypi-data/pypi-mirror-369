import logging
import os
import shutil
import traceback
import sys
from .file import createlogFilename, removeEmptyFiles, cleanFilenameWithoutExtension
from .config import DEBUG


class HandlerLoggerAfterAction(logging.Handler):
    _filename = None
    _currentFilenamePath = None
    _logsFolder = None
    def __init__(self, logsFolder, filename, currentFilenamePath):
        super().__init__()
        self._logsFolder = logsFolder
        self._filename = filename
        self._currentFilenamePath = currentFilenamePath

    def emit(self, record):
        '''
        Cette fonction permet d'executer une action après l'execution du log.
        '''
        self.post_log_action(record)
    def post_log_action(self, record):
        '''
        Cette fonction permet d'executer une action après l'écriture dans le log.
        '''
        log_entry = self.format(record)
        # print("[pyarccmder->logger.py] HandlerLoggerAfterAction - log_entry:: ", log_entry)
        
        removeEmptyFiles(self._logsFolder, ['.log'], debug=DEBUG)
        LoggerArchive(
            currentFilenamePath = self._currentFilenamePath,
            filename = self._filename,
            limit = 50,
            deleteAfter=False,
            logsFolder=self._logsFolder,
            debug = False
        )

def LoggerArchive(
    currentFilenamePath,
    filename,
    limit = 50,
    deleteAfter: bool = False,
    logsFolder: str = 'logs',
    debug = DEBUG,
):
    '''
    Cette fonction permet d'archiver le log courant dans un log archive si le nombre de ligne du fichier est egal à la limite defini

        Parameters:
            currentFilenamePath (str): le chemin du fichier log courant
            filename (str): le nom initial du fichier log
            limit (int): la limite de log par fichier
            deleteAfter (bool): supprimer le fichier courant après le transfert
            logsFolder (str): le repertoire du dossier contenant tous les logs
            debug (bool): la valeur du mode debogage ou pas
    '''
    try:
        logsFolder: str = logsFolder if type(logsFolder) == str and len(logsFolder) > 0 else 'logs'
        if filename is not None:
            deleteAfter = deleteAfter if type(deleteAfter) == bool else False
            debug = debug if type(debug) == bool else DEBUG
            loggerFilename = createlogFilename(filename, debug = debug)
            loggerFilenamePath = f"{logsFolder}/{loggerFilename}.log"
            limit = int(limit) if type(limit) in (int, float) else 50
            
            if os.path.exists(currentFilenamePath):
                with open(currentFilenamePath, 'r') as currentFile:
                    linesLength = sum(1 for _ in currentFile)
                    if linesLength >= limit:
                        shutil.copyfile(currentFilenamePath, loggerFilenamePath)
                        open(currentFilenamePath, 'w').close()
                        if deleteAfter == True:
                            os.remove(currentFilenamePath)
    except Exception as err:
        stack = traceback.format_exc()
        print("[ERROR][pyarccmder -> logger.py] LoggerArchive | stack:: ", stack)


def GetLogger(filename: str, logsFolder: str = 'logs', debug: bool = DEBUG):
    '''
    Cette fonction permet de creer le dossier de logs de notre package

        Parameters:
            filename (str): nom du fichier
            logsFolder (str): le repertoire du dossier contenant tous les logs

        Returns:
            logging.Logger: La reponse de la fonction
    '''
    
    logsFolder: str = logsFolder if type(logsFolder) == str and len(logsFolder) > 0 else 'logs'
    debug = debug if type(debug) == bool else DEBUG
    createfolderLogger(debug = debug)

    if(debug == True):
        print("[pyarccmder->logger.py] GetLogger - filename:: ", filename)

    loggerCurrentFilename = cleanFilenameWithoutExtension(
        filename=filename,
        mapCF=lambda x: "current__{data}".format(
            data = x,
        ),
        debug=debug,
    )
    loggerCurrentFilenamePath = f"{logsFolder}/{loggerCurrentFilename}.log"

    logging.basicConfig(
        level = logging.DEBUG,
        format="%(name)s %(asctime)s %(levelname)s %(message)s",
        handlers = [
            logging.FileHandler(loggerCurrentFilenamePath),
            logging.StreamHandler(),
            HandlerLoggerAfterAction(logsFolder, filename, loggerCurrentFilenamePath),
        ],
    )

    logger = logging.getLogger(filename)
    logger.setLevel(logging.INFO)

    return logger

def createfolderLogger(logsFolder: str = 'logs', debug: bool = DEBUG):
    '''
    Cette fonction permet de creer le dossier de logs de notre package

        Parameters:
            logsFolder (str): le repertoire du dossier contenant tous les logs
    '''
    logsFolder: str = logsFolder if type(logsFolder) == str and len(logsFolder) > 0 else 'logs'
    debug = debug if type(debug) == bool else DEBUG
    directory = logsFolder
    if not os.path.exists(directory):
        os.makedirs(directory)
