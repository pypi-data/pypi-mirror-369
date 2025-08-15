from setuptools import setup, find_packages

VERSION = '0.0.4' 
DESCRIPTION = "Package permettant d'implementer ses propres commandes avec des fonctionnalités spécifiques"
LONG_DESCRIPTION = "Il s'agit d'un package permet permet d'implementer ses propres commandes avec des fonctionnalités spécifiques"

# Setting up
setup(
       # the name must match the folder name 'pyarccmder'
        name="pyarccmder", 
        version=VERSION,
        author="BILONG NTOUBA Célestin",
        author_email="bilongntouba.celestin@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            "pytz;python_version>='2022.1'",
            "typing;python_version>='3.7.4.3'",
            "asyncio;python_version>='3.4.3'",
            "jonschema;python_version>='0.0.9123'",
        ],
        
        keywords=['python', 'hivi', 'pyarccmder', 'cmder'],
        classifiers= [
            # "Headless CMS :: package :: Digibehive",
        ]
)