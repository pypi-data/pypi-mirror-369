from typing import List, Optional, Callable, Any, Union
from pyarccmder import arcCmder, CmderError, DEBUG
from default_cmd_datas import lang, name, helpConfig, helpHandler, unknownConfig, unknownHandler


def generateModuleConfigFileHandler(
    lang: str,
    name: str,
    value: Any,
    config: List[dict] = None,
) -> Any:
    print(f"[*] {name.upper()}")
    print(f"[**] Generate module")
    moduleName = value
    destinationArr = [ conf for index, conf in enumerate(config) if (
        conf['name'] == 'destination'
    )]
    destination = destinationArr[0]['value'] if (
        len(destinationArr) > 0 and
        destinationArr[0]['value'] is not None
    ) else None
    idModuleArr = [ conf for index, conf in enumerate(config) if (
        conf['name'] == 'id'
    )]
    idModule = idModuleArr[0]['value'] if (
        len(idModuleArr) > 0 and
        idModuleArr[0]['value'] is not None
    ) else moduleName
    descriptionModuleArr = [ conf for index, conf in enumerate(config) if (
        conf['name'] == 'description'
    )]
    descriptionModule = descriptionModuleArr[0]['value'] if (
        len(descriptionModuleArr) > 0 and
        descriptionModuleArr[0]['value'] is not None
    ) else moduleName
    
    if destination is None:
        raise CmderError(
            ({
                'fr': f"La destination est obligatoire pour generer le module",
                'en': f"The destination is required to generate the module",
            })[lang],
            file = __name__,
            debug = DEBUG,
        )
    elif moduleName is None:
        raise CmderError(
            ({
                'fr': f"Le nom du module est obligatoire pour generer le module",
                'en': f"The module name is required to generate the module",
            })[lang],
            file = __name__,
            debug = DEBUG,
        )


    print(f"-- config:: ", config)
    print(f"-- moduleName:: ", moduleName)
    print(f"-- destination:: ", destination)
    print(f"-- idModule:: ", idModule)
    print(f"-- descriptionModule:: ", descriptionModule)


    from pyarcgenerator import arcGen

    config = {
        'name': 'pyarccore-module-generator',
        'config': {
            'author': {
                'name': 'BILONG NTOUBA',
                'firstname': 'Célestin',
                'function': 'Developpeur fullstack'
            },
            'module_name': moduleName,
            'module_id': idModule,
            'module_description': descriptionModule,
            'destination': destination,
        },
        'dest': destination,
        'struct': [
            {
                'type': 'folder',
                'name': '{{_initial_config.module_name}}',
                'config': {
                },
                'children': [
                    {
                        'type': 'file',
                        'name': 'ex3.html',
                        'content': 'lorem ipsum 2',
                        'config': {
                            'id': 'lorem2',
                            'value': 'icome 4',
                        },
                    },
                    {
                        'type': 'file',
                        'name': 'config.xml',
                        'content': """<config>
    <metadatas>
        <id>{{_initial_config.module_id}}</id>
        <name>{{_initial_config.module_name}}</name>
        <description>{{_initial_config.module_description}}</description>
        <version>0.0.0.1</version>
        <authors>
            <author>
                <name>author name</name>
                <email>author email</email>
                <position>author post</position>
                <company>author company</company>
            </author>
        </authors>
    </metadatas>
</config>""",
                        'config': {
                            'id': 'lorem2',
                            'value': 'icome 4',
                        },
                    },
                ]
            },
        ],
    }

    arcGen(
        name = name,
        config = config,
        lang = lang,
    )

    return value

config = [
    {
        "name": "generate-module-config-file",
        "shortname": "gmcf",
        "description": {
            'fr': "Cette commande permet de generer le fichier de configuration d'un module pour notre projet",
            'en': "This command generates the configuration file for a module for our project",
        },
        "hasValue": True,
        'handler': generateModuleConfigFileHandler,
    },
    {
        "name": "destination",
        "shortname": "dest",
        "description": {
            'fr': "Permet de specifier le chemin de destination du module",
            'en': "This command generates a module for our project",
        },
        "hasValue": True,
    },
    {
        "name": "id",
        "shortname": "id",
        "description": {
            'fr': "Permet de donner l'identifiant du module",
            'en': "Allows you to provide a id of the module",
        },
        "hasValue": True,
    },
    {
        "name": "description",
        "shortname": "desc",
        "description": {
            'fr': "Permet de donner la description du module",
            'en': "Allows you to provide a description of the module",
        },
        "hasValue": True,
    },
]

arcCmder(
    name = 'pyarccli-generate-module-config-file',
    config = config,
    lang = lang,
    # helpConfig=helpConfig,
    unknownConfig=unknownConfig,
)