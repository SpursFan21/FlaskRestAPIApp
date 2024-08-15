from flask import Flask, request, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Initialize app
app = Flask(__name__)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))

if 'RDS_DB_NAME' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'postgresql://{username}:{password}@{host}:{port}/{database}'.format(
            username=os.environ['RDS_USERNAME'],
            password=os.environ['RDS_PASSWORD'],
            host=os.environ['RDS_HOSTNAME'],
            port=os.environ['RDS_PORT'],
            database=os.environ['RDS_DB_NAME'],
        )
    )
else:
    # Local database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/flask_demo_api_db'

# Initialize db and migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Marshmallow
ma = Marshmallow(app)

# Users Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    
    def __init__(self, first_name, last_name, email, password, age, gender):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.age = age
        self.gender = gender

# Users Schema
class UsersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = True
        sqla_session = db.session

# Init Schema
users_schema = UsersSchema(many=True)

# Route to display the user creation form and handle user creation
@app.route('/create-user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        age = request.form.get('age', type=int)
        gender = request.form['gender']

        # Check if the user already exists
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            return render_template('create_user.html', message="User with this email already exists.")

        # Create new user and add to the database
        new_user = Users(first_name, last_name, email, password, age, gender)
        db.session.add(new_user)
        db.session.commit()

        return render_template('create_user.html', message="User created successfully.")
    
    return render_template('create_user.html')

# Route to display all users
@app.route('/all-users', methods=['GET'])
def get_users():
    all_users = Users.query.all()
    return render_template('all_users.html', users=all_users)

# Route to handle user search
@app.route('/search-users', methods=['GET'])
def search_users():
    query = request.args.get('query', '')
    users = Users.query.filter(
        (Users.first_name.ilike(f'%{query}%')) |
        (Users.last_name.ilike(f'%{query}%'))
    ).all()
    return render_template('search_user.html', users=users, query=query)

# Route to display the search user form
@app.route('/search-user', methods=['GET'])
def search_user():
    return render_template('search_user.html', users=None, query='')

# Route to display the home page
@app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(port=5000, debug=True)
