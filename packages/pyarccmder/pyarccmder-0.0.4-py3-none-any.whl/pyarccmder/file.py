import re
import os
import traceback
from datetime import datetime
from .string import RandomStr
import pytz
from .config import DEBUG


def createlogFilename(filename: str, debug: bool = DEBUG, logInterval: int = 15):
    '''
    Cette fonction permet de creer un nom de fichier log

        Parameters:
            filename (str): nom du fichier

        Returns:
            'str|None': La reponse de la fonction
    '''
    debug = debug if type(debug) == bool else DEBUG
    logInterval = int(logInterval) if type(logInterval) in (int, float) else 15
    dateAct = datetime.now(tz=pytz.UTC)
    minuteSup1 = int(dateAct.strftime('%M'))
    minuteSup1F = (str((minuteSup1 // logInterval) * logInterval) if minuteSup1 > 9 else ('0{0}'.format(minuteSup1)))
    sup1 = cleanFilenameWithoutExtension(
        filename= "{0}{1}".format(
            dateAct.strftime('%Y%m%d%H%M%S%f%Z'),
            minuteSup1F,
        ),
        debug=debug,
    )
    return cleanFilenameWithoutExtension(
        filename=filename,
        mapCF=lambda x: "{sup1}_{data}".format(
            data = x,
            sup1 = sup1,
        ),
        debug=debug,
    )
def removeEmptyFiles(directory, extensions = [], debug: bool = DEBUG):
    '''
    Cette fonction permet de supprimer tous les fichiers vide d'un repertoire

        Parameters:
            directory (str): nom du fichier

        Returns:
            'bool': La reponse de la fonction
    '''
    try:
        pass
    except Exception as err:
        stack = traceback.format_exc()
    res: bool = False
    directory = directory if(
        type(directory) == str and
        len(directory) > 0
    ) else None
    if debug == True:
        print("[pyarccmder -> file.py] removeEmptyFiles - directory:: ", directory)
    extensions = list(
        filter(
            lambda ext: (
                type(ext) == str and
                len(ext) > 0
            ),
            extensions,
        )
    ) if (
        type(extensions) in (list, tuple) and
        len(extensions) > 0
    ) else []
    if directory is not None :
        if debug == True:
            print("[pyarccmder -> file.py] removeEmptyFiles - os.listdir(directory):: ", os.listdir(directory))
            print("[pyarccmder -> file.py] removeEmptyFiles - extensions:: ", extensions)
        i = 0
        for filename in os.listdir(directory):
            if(
                len(
                    list(
                        filter(
                            lambda ext: filename.endswith(ext),
                            extensions,
                        )
                    )
                ) > 0
            ):
                file_path = os.path.join(directory, filename)
                if os.path.getsize(file_path) == 0:
                    os.remove(file_path)
                    res = True
            i = i + 1
    return res

def cleanFilenameWithoutExtension(filename: str, mapCF = lambda x: x, premap = lambda x: x, debug: bool = DEBUG):
    '''
    Cette fonction permet de creer un nom de fichier

        Parameters:
            filename (str): nom du fichier
            mapCF (def): mapping de la chaîne de caratères
            premap (def): premapping de la chaîne de caratères

        Returns:
            'str|None': La reponse de la fonction
    '''
    debug = debug if type(debug) == bool else DEBUG
    if(filename is not None):
        sep = '_'
        res = (
            premap(
                sep.join(
                    list(
                        filter(
                            lambda x: len(x) > 0,
                            re.sub(
                                re.compile(r"[^a-zA-Z0-9_]", re.MULTILINE),
                                sep,
                                filename,
                            ).split(sep),
                        )
                    )
                )
            ) if callable(premap) else (
                sep.join(
                    list(
                        filter(
                            lambda x: len(x) > 0,
                            re.sub(
                                re.compile(r"[^a-zA-Z0-9_]", re.MULTILINE),
                                sep,
                                filename,
                            ).split(sep),
                        )
                    )
                )
            )
        ) if len(filename) > 0 else None
        res = (
            mapCF(
                res
            ) if callable(mapCF) else res
        ) if len(filename) > 0 else None
        return res
    else:
        return None