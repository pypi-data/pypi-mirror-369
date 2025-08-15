import re
import json
from functools import reduce
import datetime

from .config import DEBUG, dateTimeFormatInitial, timeFormatInitial, dateFormatInitial


currentLang = 'en'
langs = ['en', 'fr']

def getLang(lang, debug = DEBUG):
    debug = debug if type(debug) == bool else DEBUG
    result = lang
    result = result if result in langs else 'fr'
    return result

def CleanName(
    value: str,
    sep: str = '_',
    regExp: str = r"[^a-zA-Z0-9_]",
    debug = DEBUG,
) -> str:
    '''
    Cette fonction permet de nettoyer un string en enlevant tous les caracteres non-alphanumeriques

        Parameters:
            value (str): element à nettoyer
            sep (str): separateur

        Returns:
            JON.Object: La reponse de la fonction
    '''
    debug = debug if type(debug) == bool else DEBUG
    if(not(
        type(value) in (str, int, float) and
        type(sep) in (str, int, float)
    )):
        return None
    value = str(value)
    sep = str(sep)
    res = sep.join(
        list(
            filter(
                lambda x: len(x) > 0,
                re.sub(
                    re.compile(regExp, re.MULTILINE),
                    sep,
                    value,
                ).split(sep),
            )
        )
    ) if len(value) > 0 else None
    return res