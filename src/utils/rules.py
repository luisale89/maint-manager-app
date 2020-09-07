'''En este archivo se definen las reglas para crear el bundle de javascript y css'''

from flask_assets import Bundle
from webassets.filter import get_filter

libsass = get_filter( #se crea un filtro a partir de libsass, con todas las configuraciones necesarias
    'libsass',
    style='nested', #parametro define el estilo de salida del bundle. En prod. debe ser 'compressed'
    # includes=['./src/static/scss'], #lista con las rutas que contienen los .scss importados en el index.scss
    # as_output=True
)

bundles = {
    'main_js': Bundle(
        'js/*.js',
        filters='jsmin',
        output='bundle/main.js' #.%(version)s
    ),
    'main_css': Bundle(
        'scss/index.scss',
        filters= [libsass], #lista de los filtros usados para este bundle.
        depends=['scss/*.scss'], #lista con las rutas a los archivos que son vigilados por el bundle y que deben ser compilados ante cualquier cambio.
        output='bundle/main.css',
    )
}