import os
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy

#Initialize the App
app=Flask(__name__)

# 2. Configuration
# PROFESSIONAL TIP: Never hardcode passwords. We read from Environment Variables.
# We default to the internal VM connection string if the var isn't set.
# Structure: postgresql://user:password@hostname/dbname
db_user = os.environ.get('POSTGRES_USER', 'myuser')
db_password = os.environ.get('POSTGRES_PASSWORD', 'mypassword')
db_host = os.environ.get('POSTGRES_HOST', 'localhost') # Localhost because DB is on same VM
db_name = os.environ.get('POSTGRES_DB', 'movies_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Initialize the DB
db = SQLAlchemy(app)


# 4. Define the Model (The Table Schema)
class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }

# 5. Create Tables (Run this once on startup)
with app.app_context():
    db.create_all()



# --- ROUTES ---

@app.route('/api/movies', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    return jsonify([movie.to_json() for movie in movies])

@app.route('/api/movies/<int:id>', methods=['GET'])
def get_movie(id):
    movie=Movie.query.get_or_404(id)
    return jsonify(movie.to_json())

@app.route('/api/movies', methods=['POST'])
def create_movie():
    data = request.get_json()
    new_movie = Movie(title=data['title'], description=data.get('description', ''))
    db.session.add(new_movie)
    db.session.commit()
    return jsonify(new_movie.to_json()), 201

@app.route('/api/movies', methods=['DELETE'])
def delete_all_movies():
    db.session.query(Movie).delete()
    db.session.commit()
    return jsonify({'message': 'All movies deleted'})

# 6. Run the server
if __name__ == '__main__':
    # Host='0.0.0.0' is CRITICAL. It tells Flask to listen on ALL network interfaces.
    # If you use 'localhost', the VM will hear it, but your Laptop won't.
    app.run(host='0.0.0.0', port=8080)