from app import app, db
from models import Pelicula, Serie, Temporada, Capitulo

def poblar_base_datos():
    with app.app_context():
        # Opcional: Limpiar datos existentes para evitar duplicados si se corre varias veces
        print("Limpiando base de datos anterior...")
        db.drop_all()
        db.create_all()

        print("Insertando películas de prueba...")
        pelicula1 = Pelicula(
            tmdb_id=101,
            titulo="El Viaje de Chihiro (Ejemplo)",
            genero="Animación, Fantasía, Aventura",
            fecha="2001-07-20",
            sinopsis="Una niña de 10 años errante tropieza con un mundo gobernado por dioses, brujas y espíritus.",
            poster="/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
            rating=8.5,
            url="https://www.youtube.com/embed/dQw4w9WgXcQ"
        )
        
        pelicula2 = Pelicula(
            tmdb_id=102,
            titulo="Interestelar (Ejemplo)",
            genero="Ciencia ficción, Drama",
            fecha="2014-11-05",
            sinopsis="Un grupo de científicos y astronautas, utilizando un agujero de gusano, buscan superar los límites en los viajes espaciales.",
            poster="/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
            rating=8.6,
            url="https://www.youtube.com/embed/dQw4w9WgXcQ"
        )

        db.session.add_all([pelicula1, pelicula2])

        print("Insertando series de prueba...")
        serie1 = Serie(
            tmdb_id=201,
            titulo="Breaking Bad (Ejemplo)",
            genero="Crimen, Drama",
            fecha="2008-01-20",
            sinopsis="Un profesor de química de secundaria diagnosticado con cáncer inoperable recurre a la fabricación y venta de metanfetamina.",
            poster="/ggFHVwStSbNi0Gf1wG1rG6oD0r.jpg",
            rating=9.5
        )

        db.session.add(serie1)
        db.session.commit() # Guardamos para que la serie obtenga su ID

        # Agregar Temporadas y Capítulos a la serie
        print("Agregando temporadas y capítulos...")
        temporada1 = Temporada(serie_id=serie1.id, numero=1)
        db.session.add(temporada1)
        db.session.commit()

        # Capítulos de la temporada 1
        capitulos_t1 = [
            Capitulo(temporada_id=temporada1.id, numero=1, titulo="Piloto", sinopsis="Presentación de Walter White.", url="https://www.youtube.com/embed/dQw4w9WgXcQ"),
            Capitulo(temporada_id=temporada1.id, numero=2, titulo="El gato está en el bolso...", sinopsis="Walt y Jesse lidian con un cadáver.", url="https://www.youtube.com/embed/dQw4w9WgXcQ"),
            Capitulo(temporada_id=temporada1.id, numero=3, titulo="Y la bolsa sin mí", sinopsis="Problemas con la distribución.", url="https://www.youtube.com/embed/dQw4w9WgXcQ")
        ]
        db.session.add_all(capitulos_t1)

        # Segunda temporada
        temporada2 = Temporada(serie_id=serie1.id, numero=2)
        db.session.add(temporada2)
        db.session.commit()

        capitulos_t2 = [
            Capitulo(temporada_id=temporada2.id, numero=1, titulo="Siete treinta y siete", sinopsis="Walt y Jesse buscan protegerse de Tuco.", url="https://www.youtube.com/embed/dQw4w9WgXcQ")
        ]
        db.session.add_all(capitulos_t2)

        db.session.commit()
        print("¡Base de datos poblada exitosamente con datos de prueba!")

if __name__ == '__main__':
    poblar_base_datos()