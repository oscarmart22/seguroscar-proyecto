import os
from datetime import datetime
from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = 'seguroscar-super-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    replies = db.relationship('Post', backref=db.backref('parent', remote_side=[id]), lazy=True, order_by='Post.timestamp.asc()')

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos inválidos"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña son requeridos"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "El usuario ya existe"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Log in automatically after registration
    session['user_id'] = new_user.id
    session['username'] = new_user.username
    return jsonify({"message": "Usuario registrado exitosamente", "username": new_user.username}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos inválidos"}), 400

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({"message": "Inicio de sesión exitoso", "username": user.username}), 200

    return jsonify({"error": "Credenciales inválidas"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({"message": "Sesión cerrada"}), 200

@app.route('/api/me', methods=['GET'])
def get_me():
    if 'user_id' in session:
        return jsonify({"logged_in": True, "username": session['username']})
    return jsonify({"logged_in": False})

@app.route('/foro')
def foro():
    return send_from_directory('.', 'foro.html')

@app.route('/api/posts', methods=['GET', 'POST'])
def api_posts():
    if request.method == 'POST':
        if 'user_id' not in session:
            return jsonify({"error": "No autenticado"}), 401
        data = request.get_json()
        content = data.get('content')
        parent_id = data.get('parent_id')
        if not content:
            return jsonify({"error": "El contenido no puede estar vacío"}), 400
        new_post = Post(user_id=session['user_id'], content=content, parent_id=parent_id)
        db.session.add(new_post)
        db.session.commit()
        return jsonify({
            "message": "Post creado",
            "post": {
                "id": new_post.id,
                "username": new_post.user.username,
                "content": new_post.content,
                "timestamp": new_post.timestamp.strftime("%Y-%m-%d %H:%M:%S") if new_post.timestamp else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "upvotes": new_post.upvotes,
                "downvotes": new_post.downvotes,
                "parent_id": new_post.parent_id,
                "replies": []
            }
        }), 201
    
    # Solo obtener posts principales (sin padre)
    posts = Post.query.filter_by(parent_id=None).order_by(Post.timestamp.desc()).all()
    
    def serialize_post(post):
        return {
            "id": post.id,
            "username": post.user.username,
            "content": post.content,
            "timestamp": post.timestamp.strftime("%Y-%m-%d %H:%M:%S") if post.timestamp else "",
            "upvotes": post.upvotes,
            "downvotes": post.downvotes,
            "parent_id": post.parent_id,
            "replies": [serialize_post(reply) for reply in post.replies]
        }

    posts_data = [serialize_post(post) for post in posts]
    return jsonify(posts_data), 200

@app.route('/api/vote', methods=['POST'])
def api_vote():
    if 'user_id' not in session:
        return jsonify({"error": "No autenticado"}), 401
    data = request.get_json()
    post_id = data.get('post_id')
    vote_type = data.get('vote_type')
    
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post no encontrado"}), 404
        
    if vote_type == 'up':
        post.upvotes += 1
    elif vote_type == 'down':
        post.downvotes += 1
    else:
        return jsonify({"error": "Tipo de voto inválido"}), 400
        
    db.session.commit()
    return jsonify({"message": "Voto registrado"}), 200

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
