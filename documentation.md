# Maintenance Manger App.

Aplicacion para la gestion del mantenimiento de activos, enfocado en sistemas de refrigeracion.

implementa base de datos en postgresql, a traves de [flask-sqlalchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) y [Redis](https://docs.redis.com/latest/rs/references/client_references/client_python/)

---

La aplicacion comenzara como un planificador de tareas, haciendo seguimiento de las actividades y permitiendo la
incorporacion de planes de mantenimiento y tareas. Luego, se realizaran implementaciones IoT, ML, etc.

--- 

**Para comenzar:**

- Crear base de datos
- Crear archivo .env en la raiz de la carpeta de la app, utilizando los parametros de ejemplo en .env.example. 
- App utiliza **pipenv** para crear entorno virtual y manejar los paquetes. Debe estar instalado en el servidor local.

## `pipenv install`
Instala los paquetes en pipfile 

## `pipenv run init`
Crea carpeta de migraciones, a traves de [Flask-migrate](https://flask-migrate.readthedocs.io/en/latest/)

## `pipenv run migrate`
Crea la primera migracion de los modelos de la base de datos

## `pipenv run upgrade`
Realiza la actualizacion de los modelos en la base de datos, creando las tablas existentes en archivo models.

## `pipenv run start`
Inicia el servidor de pruebas de flask. 