import re
from random import *
from .config import tabAlphanumerique, tabAlphabetique, tabAlphanumeriqueInsensitive, tabAlphabetiqueInsensitive, tabNumerique, DEBUG


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
def RandomStr(
    typeStr = 'alphanumeric',
    lengthStr = 20,
    variationState = False,
    mapF = lambda data: data,
    debug: bool = DEBUG,
) :
    '''
    Cette fonction permet de creer une chaîne de caractères aléatoire

        Parameters:
            typeStr (str): type de chaîne de caractères (alphanumeric, alphabetical, alphanumeric-insensitive, alphabetical-insensitive, numeric)
            lengthStr (int): nombre de caratères
            variationState (bool): chaîne de caractères variable ou pas
            mapF (def): mapping de la chaîne de caratères

        Returns:
            'str|None': La reponse de la fonction
    '''
    debug = debug if type(debug) == bool else DEBUG
    mapF = mapF if callable(mapF) else (lambda data: data)
    typesStr = ['alphanumeric', 'alphabetical', 'alphanumeric-insensitive', 'alphabetical-insensitive', 'numeric']
    typesStr_tab = {
        'alphanumeric': tabAlphanumerique,
        'alphabetical': tabAlphabetique,
        'alphanumeric-insensitive': tabAlphanumeriqueInsensitive,
        'alphabetical-insensitive': tabAlphabetiqueInsensitive,
        'numeric': tabNumerique,
    }
    typeStr = typeStr if typeStr in typesStr else typesStr[0]

    tabSelected = typesStr_tab[typeStr] if typeStr in list(typesStr_tab.keys()) else typesStr_tab[typesStr[0]]
    variationState = variationState if type(variationState) == bool else False
    if debug == True :
        print("[pyarccmder -> string] RandomStr - lengthStr:: ", lengthStr)
    lengthStr = randint(1, lengthStr) if variationState else lengthStr
    result = list(
        range(1, lengthStr + 1, 1)
    )
    result = ''.join(
        list(
            map(lambda x: choice(tabSelected), result)
        )
    )
    if type(result) in (int, float, str):
        result = mapF(result)

    return result
