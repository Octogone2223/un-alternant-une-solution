# un-alternant-une-solution (develop branch)

## for using sass
``
python manage.py sass authentication/static/styles/scss/ authentication/static/styles/css/ --watch
``

**replace by the path of your styles folder !**

## for using vue :

checkout the example at authentication/templates/sign_in.html & app/templates/base.html

## To connect to postgres database, create a .env file and place the following environment variables.

```js
DATABASE_PASSWORD=YOUR_PASSWORD
DATABASE_NAME=dbtest
DATABASE_USER=postgres
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432

```