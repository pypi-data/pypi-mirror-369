# README

**pyarccmder** est une dependance python permet d'executer des commandes consoles customisées préalablement configurées par vos soins.

## Builder le projet

### Installations préalables

* **windows** : python -m pip install sdist bdist_wheel twine
* **linux** : sudo -H pip3 install sdist bdist_wheel twine

### Builder le projet

* **windows** : python setup.py sdist bdist_wheel
* **linux** : sudo py setup.py sdist bdist_wheel

### Deployer le projet sur pip

* **windows** : python -m twine upload dist/*
* **linux** : sudo twine upload dist/*

## Git

### Cloner le projet

git init && git remote add origin https://[username]@bitbucket.org/[username]/pypyarccmder.git && git config user.email [email] && git checkout -b [branche] && git pull origin [branche]

### Pousser le projet

git checkout [branche] && git add -A && git fetch && git merge [branche] && git commit -am "[le message commit]" && git push -u origin [branche]

## Tests

* **windows** : cls && python test.py
* **linux** : clear && python test.py

## Example
cls && python test.py -h lorem1 bilong ntouba -prename2 custom --prename célestin --config=conf.json --name="title 2"

## Docstring

### Installations préalables

* **windows** : python -m pip install pdoc3
* **linux** : sudo -H pip3 install pdoc3

### Au préalable

Documenter aux préalables son code.

### Generer une documentation

* **windows** : python -m pdoc [projet]
* **linux** : sudo pdoc [projet]