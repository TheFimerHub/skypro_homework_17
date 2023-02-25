from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")
        if director_id and genre_id:
            movies = db.session.query(Movie).filter(Movie.director_id == director_id, Movie.genre_id == genre_id).all()
            return movies_schema.dump(movies), 200
        if director_id:
            movies = db.session.query(Movie).filter(Movie.director_id == director_id).all()
            return movies_schema.dump(movies)
        if genre_id:
            movies = db.session.query(Movie).filter(Movie.genre_id == genre_id)
            return movies_schema.dump(movies), 200
        else:
            movies = db.session.query(Movie).all()
            return movies_schema.dump(movies), 200

    def post(self):
        req_json = request.json
        unpack = Movie(**req_json)
        with db.session.begin(unpack):
            db.session.add(unpack)
            db.session.commit()
        return "", 201

@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        if db.session.query(Movie).get(mid):
            movie = db.session.query(Movie).get(mid)
            return movie_schema.dump(movie), 200
        else:
            return "", 404

    def post(self, mid):
        movie = db.session.query(Movie).get(mid)
        req_json = request.json
        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.year = req_json.get("year")
        movie.rating = req_json.get("rating")
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, mid):
        movie_del = db.session.query(Movie).get(mid)
        db.session.delete(movie_del)
        db.session.commit()
        return "", 204

if __name__ == '__main__':
    app.run(debug=True)
