from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db




class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Pelicula(db.Model):
    __tablename__ = 'peliculas'

    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    titulo = db.Column(db.String(255), nullable=False, index=True)
    genero = db.Column(db.String(255), nullable=True, index=True)
    fecha = db.Column(db.Text, nullable=True)
    sinopsis = db.Column(db.Text, nullable=True)
    poster = db.Column(db.Text, nullable=True)
    backdrop = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    url = db.Column(db.Text, nullable=True)
    url_extra = db.Column(db.Text, nullable=True)
    url_respaldo = db.Column(db.String(300), nullable=True) # <-- NUEVO CAMPO

    @property
    def id_tmdb(self):
        return self.tmdb_id

    @property
    def calificacion(self):
        return self.rating

    @property
    def anio(self):
        return self.fecha

    @property
    def anio_solo(self):
        return str(self.fecha)[:4] if self.fecha else ""

    @property
    def poster_url(self):
        if self.poster:
            return self.poster if self.poster.startswith('http') else f"https://image.tmdb.org/t/p/w500{self.poster}"
        return "/static/img/no-poster.png"

    @property
    def backdrop_url(self):
        if self.backdrop:
            return self.backdrop if self.backdrop.startswith('http') else f"https://image.tmdb.org/t/p/w1280{self.backdrop}"
        return ""


class Serie(db.Model):
    __tablename__ = 'series'

    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    titulo = db.Column(db.String(255), nullable=False, index=True)
    genero = db.Column(db.String(255), nullable=True, index=True)
    fecha = db.Column(db.Text, nullable=True)
    sinopsis = db.Column(db.Text, nullable=True)
    poster = db.Column(db.Text, nullable=True)
    backdrop = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, nullable=True)

    temporadas = db.relationship('Temporada', backref='serie', lazy='selectin', cascade="all, delete-orphan")

    @property
    def id_tmdb(self):
        return self.tmdb_id

    @property
    def calificacion(self):
        return self.rating

    @property
    def anio(self):
        return self.fecha

    @property
    def anio_solo(self):
        return str(self.fecha)[:4] if self.fecha else ""

    @property
    def poster_url(self):
        if self.poster:
            return self.poster if self.poster.startswith('http') else f"https://image.tmdb.org/t/p/w500{self.poster}"
        return "/static/img/no-poster.png"

    @property
    def backdrop_url(self):
        if self.backdrop:
            return self.backdrop if self.backdrop.startswith('http') else f"https://image.tmdb.org/t/p/w1280{self.backdrop}"
        return ""


class Temporada(db.Model):
    __tablename__ = 'temporadas'

    id = db.Column(db.Integer, primary_key=True)
    serie_id = db.Column(db.Integer, db.ForeignKey('series.id', ondelete='CASCADE'), nullable=False, index=True)
    numero = db.Column(db.Integer, nullable=False)

    capitulos = db.relationship('Capitulo', backref='temporada', lazy='selectin', cascade="all, delete-orphan", order_by="Capitulo.numero")


class Capitulo(db.Model):
    __tablename__ = 'capitulos'

    id = db.Column(db.Integer, primary_key=True)
    temporada_id = db.Column(db.Integer, db.ForeignKey('temporadas.id', ondelete='CASCADE'), nullable=False, index=True)
    numero = db.Column(db.Integer, nullable=False)
    titulo = db.Column(db.Text, nullable=True)
    backdrop = db.Column(db.String(255), nullable=True)  # O el tipo de dato que estés usando
    fecha = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)
    url_extra = db.Column(db.Text, nullable=True)
    url_respaldo = db.Column(db.String(300), nullable=True) # <-- NUEVO CAMPO