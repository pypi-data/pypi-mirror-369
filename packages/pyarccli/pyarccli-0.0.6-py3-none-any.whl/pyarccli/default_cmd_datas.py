from typing import List, Optional, Callable, Any, Union


lang = "en"
name = 'pyarccli'

def helpHandler(
    lang: str,
    name: str,
    value: Any,
    config: List[dict] = None,
) -> Any: 
    return value
helpConfig = {
    'name': "help",
    'shortname': "he",
    'description': {
        'fr': "CUSTOM - Permet d'afficher toutes les commandes disponibles",
        'en': "CUSTOM - Displays all available commands",
    },
    'demo': [
        f"{name} -he",
        f"{name} --help",
    ],
    'hasValue': False,
    'handler': helpHandler,
}
def unknownHandler(
    lang: str,
    name: str,
    value: Any,
    config: List[dict] = None,
) -> Any:
    # print(f"[*] {name.upper()}")
    # print(f"-- UNKNOWN ACTION --")
    return value
unknownConfig = {
    'name': "unknown",
    'shortname': "unk",
    'description': {
        'fr': "tous les arguments non répertoriés",
        'en': "all arguments not listed",
    },
    'hasValue': False,
    'handler': unknownHandler,
}