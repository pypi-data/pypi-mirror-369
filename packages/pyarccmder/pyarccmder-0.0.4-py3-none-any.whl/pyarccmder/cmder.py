from typing import List, Optional, Callable, Any, Union
import inspect
import asyncio
import logging
import traceback
import sys
import re
import json
import jon as JON

from .config import DEBUG
from .utils import getLang
from .exception import CmderError


def helpHandler(
    lang: str,
    name: str,
    value: Any,
    config: List[dict] = None,
) -> Any:
    targetConfig = next(
        iter(tuple(
            filter(
                lambda x: (
                    value is not None and (
                        x['name'] == value or
                        x['shortname'] == value
                    )
                ),
                config,
            ),
        )),
        None
    )
    if DEBUG:
        print("[arc-cmder.ts] helpHandler | config:: ", config)
        print("[arc-cmder.ts] helpHandler | value:: ", value)
        print("[arc-cmder.ts] helpHandler | targetConfig:: ", targetConfig)
    def cleanConfData(cnf, isSingle: bool = False):
        isSingle = isSingle if type(isSingle) == bool else False
        print({
            'fr': f"{'- ' if not(isSingle == True) else ''}La commande \"{cnf['name']}\" (-{cnf['shortname']} ou --{cnf['name']}): {cnf['description'][lang]}",
            'en': f"{'- ' if not(isSingle == True) else ''}The \"{cnf['name']}\" command (-{cnf['shortname']} or --{cnf['name']}): {cnf['description'][lang]}",
        }[lang])
        if (
            type(cnf) == dict and
            'demo' in tuple(cnf.keys()) and
            cnf['demo']
        ):
            for ex in cnf['demo']:
                print(f"\t ex: {ex}")
    if config:
        print(f"[*] {name.upper()}")
        if value is not None and targetConfig is None:
            print({
                'fr': f'[ERREUR] le paramètre de configuration `{value}` est incorrecte',
                'en': f'[ERROR] the configuration parameter `{value}` is incorrect.',
            }[lang])
        else:
            if targetConfig is None:
                for confData in config:
                    cleanConfData(confData)
            else:
                confData = targetConfig
                cleanConfData(confData, True)
    return value

def getConfigSchema(lang='fr'):
    def handlerValidator(value):
        checker = (
            not value or (
                callable(value) and
                len((inspect.getfullargspec(value)).args) == 4
            )
        )
        return bool(checker)
    def handlerValidatorSanitizer(value):
        checker = (
            not value or (
                callable(value) and
                len((inspect.getfullargspec(value)).args) == 4
            )
        )
        return value if checker else None

    return JON.Object(lang).struct({
        'name': JON.String(lang).required().min(1),
        'description': JON.ChosenType(lang).choices(
            JON.String(lang).min(1).required().applyMapping(lambda dt: {
                'fr': dt,
                'en': dt,
            }),
            JON.Object(lang).struct({
                'fr': JON.String(lang).min(1).required(),
                'en': JON.String(lang).min(1).required(),
            }).required(),
        ).required(),
        'shortname': JON.String(lang).min(1),
        'hasValue': JON.Boolean(lang),
        'handler': JON.AnyType(lang).applyApp(
            rule = handlerValidator,
            sanitize = handlerValidatorSanitizer,
        ),
    }).required()

def getConfigsSchemas(lang: str = 'fr'):
    def applyMapping(vals: List[dict]) -> List[dict]:
        if vals is None:
            return []

        def defaultHandler(
            lang: str,
            name: str, value: Any, config: List[dict] = None) -> Any:
            return value

        return [
            {
                **val,
                'shortname': val['shortname'] if isinstance(val['shortname'], str) and len(val['shortname']) > 0 else val['name'][0],
                'hasValue': val['hasValue'] if isinstance(val['hasValue'], bool) else True,
                'handler': val['handler'] if (
                    callable(val['handler']) and
                    len((inspect.getfullargspec(val['handler'])).args) == 4
                ) else defaultHandler,
            }
            for val in vals
        ]

    return JON.Array(lang).types(
        getConfigSchema(lang)
    ).required().min(1).label('configs').applyMapping(applyMapping)
    # .defaultError({
    #     'fr': 'Les paramètres de configuration de la commande sont incorrects',
    #     'en': 'The configuration parameters of the command are incorrect in SASS, execute only the @for and @if and keep the rest of the SASS code'
    # })
def getCleanedConfigs(config: List[dict], lang: str = 'fr') -> List[dict]:
    schema = getConfigsSchemas(lang)
    validation = schema.validate(config)
    if validation and validation['error']:
        raise validation['error']
    return validation['data'] if validation else []

def isFilePath(path: str) -> bool:
    """
    Vérifie si le chemin donné est un chemin de fichier.

    Args:
        path (str): Le chemin à vérifier.

    Returns:
        bool: True si le chemin est un chemin de fichier, False sinon.
    """
    # Expression régulière pour vérifier si le chemin est un fichier
    filePathRegex = re.compile(r'^[A-Z]:\\(?:[^\\\/:*?"<>|\r\n]+\\)*[^\\\/:*?"<>|\r\n]+$', re.IGNORECASE)
    return bool(filePathRegex.match(path))

def isDirectoryPath(path: str) -> bool:
    """
    Vérifie si le chemin donné est un chemin de dossier.

    Args:
        path (str): Le chemin à vérifier.

    Returns:
        bool: True si le chemin est un chemin de dossier, False sinon.
    """
    # Expression régulière pour vérifier si le chemin est un dossier
    directoryPathRegex = re.compile(r'^[A-Z]:\\(?:[^\\\/:*?"<>|\r\n]+\\)*$', re.IGNORECASE)
    return bool(directoryPathRegex.match(path))

def getAllArgs() -> List[dict]:
    """
    Cette fonction permet de récupérer les arguments brutes envoyés.

    Returns:
        List[dict]: Liste des arguments avec leurs indices.
    """
    allArgs: List[dict] = []

    for index, val in enumerate(sys.argv):
        allArgs.append({
            'index': index,
            'value': val,
        })

    return allArgs
def cleanArgs(args: List[dict], config: List[dict]) -> List[dict]:
    """
    Cette fonction permet de ressortir les véritables arguments avec leurs valeurs.

    Args:
        args (List[dict]): Les arguments initiaux.
        config (List[dict]): La configuration.

    Returns:
        List[dict]: Les arguments nettoyés.
    """
    if not isinstance(args, list):
        args = []

    resInitial: List[dict] = []
    currentName: str = None

    for arg in args:
        value = arg['value']
        if value.startswith('--'):
            parts = value.split('=')
            if len(parts) == 2:
                name = parts[0][2:]
                val = parts[1].strip('\'"')
                currentName = name
                resInitial.append({'name': name, 'value': val})
            else:
                name = value[2:]
                currentName = name
                resInitial.append({'name': name, 'value': None})
        elif value.startswith('-'):
            name = value[1:]
            currentName = name
            resInitial.append({'name': name, 'value': None})
        else:
            target = next((dt for dt in resInitial if dt['name'] == currentName), None)
            keysResInitial = [dt['name'] for dt in resInitial]
            if currentName and currentName in keysResInitial and target:
                target['value'] = ' '.join(filter(lambda dt: isinstance(dt, str) and len(dt) > 0, [target['value'] or '', value]))
                resInitial = [dt for dt in resInitial if dt['name'] != currentName]
                resInitial.append(target)
            else:
                resInitial.append({'name': None, 'value': value})

    firstPosIfIsNotPathDatas = [indexDt if (
        dt['value'] and
        not isFilePath(dt['value']) and
        not isDirectoryPath(dt['value'])
    ) else None for indexDt, dt in enumerate(resInitial)]
    firstPosIfIsNotPath = next((dt for dt in firstPosIfIsNotPathDatas if isinstance(dt, int)), None)
    resInitial = [elmt for indexElmt, elmt in enumerate(resInitial) if firstPosIfIsNotPath is None or indexElmt >= firstPosIfIsNotPath]

    res: List[dict] = []
    resKeys: List[str] = []

    for dataRi in resInitial:
        valueRi = dataRi['value']
        realKeyRi = dataRi['name']
        keyRi = realKeyRi or 'unknown'
        finalConfig = next((conf for conf in config if conf['name'] == keyRi or conf['shortname'] == keyRi), None)
        if keyRi not in resKeys and finalConfig:
            resKeys.append(finalConfig['name'])
            if not realKeyRi:
                firstPosIfIsNotPathDatas = [indexDt if (
                    dt['value'] and
                    not isFilePath(dt['value']) and
                    not isDirectoryPath(dt['value'])
                ) else None for indexDt, dt in enumerate([elmt for elmt in resInitial if not elmt['name']])]
                firstPosIfIsNotPath = next((dt for dt in firstPosIfIsNotPathDatas if isinstance(dt, int)), None)
                unknownDatas = [elmt['value'] or '' for indexElmt, elmt in enumerate(resInitial) if not elmt['name'] and (firstPosIfIsNotPath is None or indexElmt >= firstPosIfIsNotPath)]
                unknownValue = ' '.join(unknownDatas) if unknownDatas else None
                res.append({'name': finalConfig['name'], 'value': unknownValue})
            else:
                res.append({'name': finalConfig['name'], 'value': valueRi})

    return res

def getConfigForValidation(
    config: List[dict],
    lang: str = 'fr'
) -> JON.Array:
    """
    Cette fonction permet de récupérer la configuration pour la validation.

    Args:
        config (List[dict]): La configuration.
        lang (str): La langue ('fr' ou 'en').

    Returns:
        JON.Array: La configuration validée.
    """
    confs = config if isinstance(config, list) else []
    return JON.Array(lang).types(
        JON.Object(lang).struct({
            "name": JON.String(lang).required().min(1),
            'value': JON.String(lang).min(1),
        }).applyMapping(lambda dtt: {
            **dtt,
            'shortname': next((conf['shortname'] for conf in config if (
                'name' in tuple(conf.keys()) and
                'shortname' in tuple(conf.keys()) and
                conf['name'] == dtt['name'] or
                conf['shortname'] == dtt['name']
            )), None),
            'description': next((conf['description'] for conf in config if (
                'description' in tuple(conf.keys()) and
                'name' in tuple(conf.keys()) and
                'shortname' in tuple(conf.keys()) and
                conf['name'] == dtt['name'] or
                conf['shortname'] == dtt['name']
            )), None),
            'demo': next((conf['demo'] for conf in config if (
                'demo' in tuple(conf.keys()) and
                'name' in tuple(conf.keys()) and
                'shortname' in tuple(conf.keys()) and
                conf['name'] == dtt['name'] or
                conf['shortname'] == dtt['name']
            )), None),
            'handler': next((conf['handler'] for conf in config if (
                'handler' in tuple(conf.keys()) and
                'name' in tuple(conf.keys()) and
                'shortname' in tuple(conf.keys()) and
                conf['name'] == dtt['name'] or
                conf['shortname'] == dtt['name']
            )), None),
        })
    ).applyMapping(lambda value: value).required().min(1).label('validation')
    # .defaultError({
    #     'fr': 'Echec lors de la validation des paramètres de configuration',
    #     'en': 'Failed to validate configuration parameters'
    # })
def executeCmds(
    name: str,
    config: List[dict],
    args: List[dict],
    lang: str = 'fr',
    helpConfig: dict = None,
    unknownConfig: dict = None,
):
    """
    Cette fonction permet d'exécuter les commandes.

    Args:
        name (str): Le nom de la commande.
        config (List[dict]): La configuration.
        args (List[dict]): Les arguments.
        lang (str): La langue ('fr' ou 'en').
        helpConfig (dict): La configuration d'aide.
        unknownConfig (dict): La configuration inconnue.
    """
    cleaned_config = [dt for dt in config if unknownConfig is None or dt['name'] != unknownConfig['name']]
    configValidationSchema = getConfigForValidation(config, lang)
    configValidation = configValidationSchema.validate(args)

    if configValidation and configValidation['error']:
        raise configValidation['error']

    assets: List[dict] = configValidation['data']
    if DEBUG:
        print("[arc-cmder.ts] executeCmds | assets:: ", assets)
    for asset_data in assets:
        if asset_data['handler']:
            asset_data['handler'](lang, name, asset_data.get('value'), cleaned_config)

def arcCmder(
    name: str,
    config: List[dict],
    lang: str = 'fr',
    helpConfig: dict = None,
    unknownConfig: dict = None,
) -> None:
    '''
    Cette fonction permet d'initialiser le gestionnaire de commandes
    '''
    try:
        helpConfigInitial = {
            'name': "help",
            'shortname': "h",
            'description': {
                'fr': "Permet d'afficher toutes les commandes disponibles",
                'en': "Displays all available commands",
            },
            'demo': [
                f"{name} -h",
                f"{name} --help",
            ],
            'hasValue': False,
            'handler': helpHandler,
        }
        helpConfig2 = getConfigSchema(lang).sanitize(helpConfig)
        if helpConfig2 is not None:
            helpConfig['name'] = helpConfigInitial['name']
            helpConfig['handler'] = helpConfigInitial['handler']
            helpConfig['hasValue'] = helpConfigInitial['hasValue']
            if 'description' in tuple(helpConfig2.keys()):
                helpConfig['description'] = helpConfig2['description']
            if 'shortname' in tuple(helpConfig2.keys()):
                helpConfig['shortname'] = helpConfig2['shortname']
            if 'demo' in tuple(helpConfig2.keys()):
                helpConfig['demo'] = helpConfig2['demo']
        else:
            helpConfig = helpConfigInitial
        if DEBUG:
            print("""[pyarccmder -> cmder.py] arcCmder | helpConfig2:: """, helpConfig2)
            print("""[pyarccmder -> cmder.py] arcCmder | helpConfig:: """, helpConfig)

        
        unknownConfigHandler = getConfigSchema(lang).sanitize(unknownConfig)['handler'] if unknownConfig else None
        unknownConfig = {
            'name': "unknown",
            'shortname': "unk",
            'description': {
                'fr': "tous les arguments non répertoriés",
                'en': "all arguments not listed",
            },
            'hasValue': False,
            'handler': (unknownConfigHandler if unknownConfigHandler else lambda lang, name, value, config: value),
        }
        if DEBUG:
            print("[arc-cmder.ts] initCmder | unknownConfigHandler:: ", unknownConfigHandler)

        cleanedConfig = getCleanedConfigs(config, lang)
        
        targetHelpConfig = next(
            iter(tuple(
                filter(
                    lambda dt: (
                        dt['name'] == 'help'
                    ),
                    cleanedConfig,
                ),
            )),
            None
        )
        if targetHelpConfig is not None:
            if 'description' in tuple(helpConfig.keys()):
                targetHelpConfig['description'] = helpConfig['description']
            if 'shortname' in tuple(helpConfig.keys()):
                targetHelpConfig['shortname'] = helpConfig['shortname']
            if 'demo' in tuple(helpConfig.keys()):
                targetHelpConfig['demo'] = helpConfig['demo']
            helpConfig = targetHelpConfig
        cleanedConfig = tuple(
            filter(
                lambda dt: not(dt['name'] in ('help', 'unknown')),
                cleanedConfig,
            ),
        )
        cleanedConfig = [
            helpConfig,
            *cleanedConfig,
            unknownConfig,
        ]
        if DEBUG:
            print("[arc-cmder.ts] initCmder | targetHelpConfig:: ", targetHelpConfig)
            print("[arc-cmder.ts] initCmder | cleanedConfig:: ", cleanedConfig)
        initialArgs = getAllArgs()
        if DEBUG:
            print("[arc-cmder.ts] initCmder | initialArgs:: ", initialArgs, '\n')
        
        args = cleanArgs(initialArgs, cleanedConfig)
        if DEBUG:
            print("[arc-cmder.ts] initCmder | args:: ", args)

        
        executeCmds(name, cleanedConfig, args, lang, helpConfig, unknownConfig)
    except Exception as err:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]

        error = CmderError(
            stack,
            file = __name__,
            debug = DEBUG,
        )
        raise error