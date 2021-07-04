* Auth microservice - base app

Aplicacion para implementar validacion de usuarios, con la posibilidad de interactuar a través de HTTP API requests.

implementa base de datos en postgresql, a traves de Flask-sqlalchemy

Para comenzar,

- pipenv install
Crear base de datos y actualizar .env en la raiz de la carpeta de la app, utilizando los parametros de ejemplo en
.env.example. 

- pipenv run migrate
Crea carpeta de migraciones, Alembic based.

- pipenv run upgrade
Realiza la actualizacion de los modelos en la base de datos, creando las tablas existentes en archivo models.

- pipenv run start.
Inicia el servidor de pruebas de flask. 

---

La aplicacion contiene paquetes que son opcionales, y que deberian eliminarse para entrar en produccion:

1. Flask-admin: se utiliza para tener facil acceso a los modelos de la base de datos, deberia eliminarse en produccion, o proteger todas las vistas con usuario y contrasena.

