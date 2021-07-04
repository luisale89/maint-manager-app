# Maintenance Manger App.

Aplicacion para la gestion del mantenimiento de activos, enfocado en sistemas de refrigeracion
implementa base de datos en postgresql, a traves de Flask-sqlalchemy

Para comenzar,

## pipenv install

Crear base de datos y actualizar .env en la raiz de la carpeta de la app, utilizando los parametros de ejemplo en
.env.example. 

## pipenv run migrate

Crea carpeta de migraciones, Alembic based.

## pipenv run upgrade

Realiza la actualizacion de los modelos en la base de datos, creando las tablas existentes en archivo models.

## pipenv run start.

Inicia el servidor de pruebas de flask. 

---

La aplicacion comenzara como un planificador de tareas, haciendo seguimiento de las actividades y permitiendo la
incorporacion de planes de mantenimiento y tareas. Luego, se realizaran implementaciones IoT, ML, etc.
