import os
from flask import Flask, render_template, request, abort, redirect, url_for, session
from sqlalchemy import event
from sqlalchemy.orm import selectinload
from extensions import db, login_manager

app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-secreta-temporal-render')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Inicializar extensiones
db.init_app(app)
login_manager.init_app(app)

# Importar modelos al final para evitar importaciones circulares
from models import Usuario, Pelicula, Serie, Temporada, Capitulo



@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))



# --- RUTA 0: Login Falso (Vista Inicial) ---
@app.before_request
def requerir_login():
    # Incluimos 'ping' para que cron-job.org pueda acceder sin autenticación
    rutas_libres = ['login', 'static', 'ping']
    if request.endpoint and request.endpoint not in rutas_libres:
        if not session.get('autenticado'):
            return redirect(url_for('login'))

@app.route('/ping', methods=['GET', 'HEAD'])
def ping():
    return 'OK', 200

@app.route('/logout')
def logout():
    session.pop('autenticado', None)
    return redirect(url_for('login'))

@app.before_request
def requerir_login():
    # Rutas libres de login (archivos estáticos y la propia vista de login)
    rutas_libres = ['login', 'static']
    if request.endpoint and request.endpoint not in rutas_libres:
        if not session.get('autenticado'):
            return redirect(url_for('login'))

# --- RUTA 1: Inicio (Listado de Películas) ---
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    peliculas_pagination = Pelicula.query.order_by(Pelicula.id.desc()).paginate(
        page=page, per_page=18, error_out=False
    )
    return render_template(
        'index.html', 
        peliculas=peliculas_pagination.items, 
        pagination=peliculas_pagination
    )


# --- RUTA 2: Listado de Series ---
@app.route('/series')
def series():
    page = request.args.get('page', 1, type=int)
    series_pagination = Serie.query.order_by(Serie.id.desc()).paginate(
        page=page, per_page=18, error_out=False
    )
    return render_template(
        'series.html', 
        series=series_pagination.items, 
        pagination=series_pagination
    )


# --- RUTA 3: Detalle y Reproductor de Película ---
@app.route('/pelicula/<int:pelicula_id>')
def detalle_pelicula(pelicula_id):
    pelicula = Pelicula.query.get_or_404(pelicula_id)
    
    reproductores = {}
    
    # Fuentes personalizadas de la base de datos (solo si tienen contenido)
    if hasattr(pelicula, 'url') and pelicula.url and pelicula.url.strip():
        reproductores["Latino Opc1"] = pelicula.url.strip()
        
    if hasattr(pelicula, 'url_extra') and pelicula.url_extra and pelicula.url_extra.strip():
        reproductores["Latino Opc2"] = pelicula.url_extra.strip()
        
    if hasattr(pelicula, 'url_respaldo') and pelicula.url_respaldo and pelicula.url_respaldo.strip():
        reproductores["Latino Opc3"] = pelicula.url_respaldo.strip()
        
    # Opciones de APIs externas si tiene TMDB ID
    if pelicula.tmdb_id:
        tmdb = pelicula.tmdb_id
        reproductores["Subtitulado Opc1"] = f"https://vidsrc.sh/embed/movie/{tmdb}"
        reproductores["Subtitulado Opc2"] = f"https://vidrock.net/movie/{tmdb}"
        reproductores["Subtitulado Opc3"] = f"https://vidfast.vc/movie/{tmdb}"
        
    return render_template('detalle_pelicula.html', pelicula=pelicula, reproductores=reproductores)


# --- RUTA 4: Detalle de Serie (Temporadas y Capítulos) ---
@app.route('/serie/<int:serie_id>')
def detalle_serie(serie_id):
    serie = Serie.query.options(
        selectinload(Serie.temporadas).selectinload(Temporada.capitulos)
    ).filter_by(id=serie_id).first_or_404()
    
    return render_template('detalle_serie.html', serie=serie)


# --- RUTA 5: Reproductor de Capítulo de Serie ---
@app.route('/capitulo/<int:capitulo_id>')
def ver_capitulo(capitulo_id):
    capitulo = Capitulo.query.get_or_404(capitulo_id)
    temporada = Temporada.query.get_or_404(capitulo.temporada_id)
    serie = Serie.query.get_or_404(temporada.serie_id)
    
    reproductores = {}
    
    # Fuentes personalizadas del capítulo (solo si tienen contenido)
    if hasattr(capitulo, 'url') and capitulo.url and capitulo.url.strip():
        reproductores["Latino Opc1"] = capitulo.url.strip()
        
    if hasattr(capitulo, 'url_extra') and capitulo.url_extra and capitulo.url_extra.strip():
        reproductores["Latino Opc2"] = capitulo.url_extra.strip()
        
    if hasattr(capitulo, 'url_respaldo') and capitulo.url_respaldo and capitulo.url_respaldo.strip():
        reproductores["Latino Opc3"] = capitulo.url_respaldo.strip()
        
    # Opciones de APIs externas por serie/temporada/episodio
    if serie.tmdb_id:
        tmdb = serie.tmdb_id
        t = temporada.numero
        c = capitulo.numero
        reproductores["Subtitulado Opc1"] = f"https://vidsrc.sh/embed/tv/{tmdb}/{t}/{c}"
        reproductores["Subtitulado Opc2"] = f"https://vidrock.net/tv/{tmdb_id}/{tmdb}/{t}/{c}"
        reproductores["Subtitulado Opc2"] = f"https://vidfast.vc/tv/{tmdb}/{t}/{c}?autoPlay=true"

    return render_template('ver_capitulo.html', capitulo=capitulo, temporada=temporada, serie=serie, reproductores=reproductores)

@app.route('/buscar')
def buscar():
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('index'))
    
    # 1. Buscar en la tabla/modelo de Películas (ejemplo con SQLAlchemy)
    resultados_peliculas = Pelicula.query.filter(Pelicula.titulo.ilike(f'%{query}%')).all()
    
    # 2. Buscar en la tabla/modelo de Series
    resultados_series = Serie.query.filter(Serie.titulo.ilike(f'%{query}%')).all()
    
    # 3. Renderizar la plantilla enviando ambas listas
    return render_template(
        'buscar.html', 
        query=query, 
        peliculas=resultados_peliculas, 
        series=resultados_series
    )


# Contexto para crear tablas limpias
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)