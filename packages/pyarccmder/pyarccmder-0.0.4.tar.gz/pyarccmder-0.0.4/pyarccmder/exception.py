import logging
import traceback
from .logger import GetLogger
from .utils import getLang
from .config import DEBUG


defaultMessageInitial = {
    'fr': "une erreur query interne s'est declenchée",
    'en': "an internal query error has occurred",
}
class Error(Exception):
    '''
    Cette classe est l'exception parent qui sera generée en cas d'erreur
    '''
    logger = None
    logType = logging.CRITICAL
    defaultMessage = defaultMessageInitial
    _debug: bool = DEBUG
    _fileName: str = None
    _lang: str = None
    _message: str = None
    _displayMessage: str = None

    def __init__(self, *args, **kwargs):
        self._debug = kwargs['debug'] if (
            'debug' in tuple(kwargs.keys()) and
            type(kwargs['debug']) == bool
        ) else True
        fileName = kwargs['file'] if (
            'file' in tuple(kwargs.keys()) and
            type(kwargs['file']) == str and
            len(kwargs['file']) > 0
        ) else __name__
        self._fileName = fileName
        lang = getLang(kwargs['lang'], debug = self._debug) if (
            'lang' in tuple(kwargs.keys())
        ) else 'fr'
        self._lang = lang
        message = args[0] if (
            type(args) == tuple and
            len(args) > 0
        ) else self.defaultMessage[lang]
        if(
            type(message) == dict and
            lang in tuple(message.keys())
        ):
            message = message[lang]
        self._message = message
        displayMessage = kwargs['displayMessage'] if (
            type(kwargs) == dict and
            'displayMessage' in tuple(kwargs.keys())
        ) else message
        if(
            type(displayMessage) == dict and
            lang in tuple(displayMessage.keys())
        ):
            displayMessage = displayMessage[lang]
        self._displayMessage = displayMessage

        print("[pyarccmder->exception] Error - message:: ", message)
        if(self._debug == True):
            print("[pyarccmder->exception] Error - __name__:: ", __name__)
            print("[pyarccmder->exception] Error - message:: ", message)

        self.logger = GetLogger(fileName, debug = self._debug)
        self.logger.setLevel(self.logType)
        self.logger.critical(message)

        if(self._debug == True):
            print("[pyarccmder->exception] Error - args:: ", args)
        argsF: list = []
        if(
            type(args) in (list, tuple) and
            len(args) > 0
        ):
            argsF = list(args)
            argsF[0] = displayMessage
        else:
            argsF.append(displayMessage)
        kwargsF: dict = {}
        if(type(kwargs) == dict):
            kwargsF = kwargs
        kwargsF['message'] = displayMessage
        if not argsF: argsF = (displayMessage,)

        # Call super constructor
        super().__init__(*tuple(argsF))

    def getDatas(self,):
        '''
        Cette fonction pernet de retourner toutes les données de l'erreur

            Returns:
                dict: La reponse de la fonction
        '''
        return {
            'filename': self._fileName,
            'lang': self._lang,
            'message': self._message,
            'displayMessage': self._displayMessage,
        }

class InternalError(Error):
    '''
    Cette classe est genère une exception en cas d'erreur interne
    '''
    logType = logging.CRITICAL
    defaultMessage = defaultMessageInitial

class TransformError(Error):
    '''
    Cette classe est genère une exception en cas d'echec de transformation de texte
    '''
    logType = logging.CRITICAL
    defaultMessage = {
        'fr': "une erreur query interne s'est declenchée",
        'en': "an internal query error has occurred",
    }

class CmderError(Error):
    '''
    Cette classe est genère une exception en cas d'echec lors de l'execution d'une commande
    '''
    logType = logging.CRITICAL
    defaultMessage = {
        'fr': "une erreur query interne s'est declenchée",
        'en': "an internal query error has occurred",
    }


def returnTrueExceptionType(
    exception: InternalError,
    ReturnType: type[InternalError] = InternalError,
    traceback: str = None,
):
    '''
    Cette fonction pernet de retourner la veritable exception

        Parameters:
            exception (Error): l'exception de depart
            ReturnType (type[InternalError]): le type d'erreur final
            traceback (str): le message complet d'erreur

        Returns:
            dict: La reponse de la fonction
    '''
    exceptionF = None
    ReturnType = ReturnType if ReturnType in [
        InternalError,
        CmderError,
    ] else InternalError
    if(
        type(exception) in [
            InternalError,
            CmderError,
        ]
    ):
        exceptionDatas = exception.getDatas()
        exceptionF = ReturnType(
            exceptionDatas['message'],
            lang = exceptionDatas['lang'],
            file = exceptionDatas['filename'],
            displayMessage = exceptionDatas['displayMessage'],
        )
    elif type(exception) == Exception and type(traceback) == str:
        exceptionF = ReturnType(
            traceback,
        )
    else:
        exceptionF = ReturnType(
            defaultMessageInitial,
        )
    return exceptionF