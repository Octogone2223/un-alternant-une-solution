# un-alternant-une-solution (develop branch)

## Introduction

Dans le cadre du cours de Web full stack à Ynov Nantes, il nous a été demandé, à nous étudiant en Mastère développemnt Web, de répondre à un appel à projets étudiants, en proposant un projet innovant.  
Notre solution consiste donc à créer un pont entre les écoles, les étudiants, et les entreprises à travers une plateforme web. Des informations telles que les profils d’étudiants, des offres d’alternances ou de formation y seront accessibles.  
Pour répondre à cet appel, nous avons mis sur pied une équipe que nous avons appelée [SkillMatch](https://github.com/SkillMatch-Team). SkillMatch est constituée de quatre étudiants alternants développeurs Web :

[Yann Kotto](https://github.com/prynge) en tant que Product Owner,  
[Kassai Kaym](https://github.com/TheYMK) en tant que Scrum Master,  
[Tom Leveque](https://github.com/tleveke) et [Lilian Ouvrard](https://github.com/Lilian-MMI) en tant que développeurs.

Le cours a été dispensé par [Antoine NGUYEN](https://github.com/tonioo).

---

## Initialisation

### Pre-requis

- Python 3.9 ou ultérieur

- Postgres Database

- [Celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html)

- [Redis](https://redis.io/)




### Installations

1. Installer les dépendences
  `pip install -r requirements.txt`

2. Ajouter les variables d'environnement dans un fichier .env à la racine du projet

  ```bin
    DATABASE_PASSWORD=YOUR_DATABASE_PASSWORD
    DATABASE_USER=YOUR_DATABASE_USERNAME
    DATABASE_NAME=YOUR_DATABASE_NAME
    DATABASE_HOST=YOUR_DATABASE_HOST
    DATABASE_PORT=YOUR_DATABASE_PORT (5432 is default)
  ```

3. Lancer une migration la base de données

  ```sh
    python manager.py migrate
  ```

4. Lancer l'application
  ```sh
    python manager.py runserver
  ```
  L'application tourne maintenant à l'adresse `localhost:8000` ou `127.0.0.1:8000`

---

## À des fins de développement

### Pour l'utilisation de sass

```sh
  python manage.py sass authentication/static/styles/scss/ authentication/static/styles/css/ --watch
```

**Remplacer le chemin de votre dossier de styles !**

## Pour l'utilisation de vue

Regarder l'exemple au niveau de `authentication/templates/sign_in.html` et de `app/templates/base.html`
