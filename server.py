import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'seguroscar-super-secret-key-123')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── Models ───

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
    replies = db.relationship(
        'Post',
        backref=db.backref('parent', remote_side=[id]),
        lazy=True,
        order_by='Post.timestamp.asc()'
    )

# ─── DB Init + Migration ───

with app.app_context():
    db.create_all()
    # Migrate: ensure parent_id column exists in posts table
    try:
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(post)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'parent_id' not in columns:
            cursor.execute("ALTER TABLE post ADD COLUMN parent_id INTEGER REFERENCES post(id)")
            conn.commit()
            print("[MIGRATION] Added parent_id column to post table.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[MIGRATION WARNING] {e}")

# ─── Global error handler: ALWAYS return JSON ───

@app.errorhandler(Exception)
def handle_exception(e):
    code = getattr(e, 'code', 500)
    return jsonify({"error": str(e)}), code

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Error interno del servidor"}), 500

# ─── Routes ───

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Datos inválidos"}), 400
    if not data:
        return jsonify({"error": "Datos inválidos"}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

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
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Datos inválidos"}), 400
    if not data:
        return jsonify({"error": "Datos inválidos"}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

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

# ─── Forum API ───

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

@app.route('/api/posts', methods=['GET', 'POST'])
def api_posts():
    if request.method == 'POST':
        if 'user_id' not in session:
            return jsonify({"error": "No autenticado"}), 401
        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({"error": "Datos inválidos"}), 400

        content = data.get('content', '').strip() if data else ''
        parent_id = data.get('parent_id') if data else None

        if not content:
            return jsonify({"error": "El contenido no puede estar vacío"}), 400

        new_post = Post(user_id=session['user_id'], content=content, parent_id=parent_id)
        db.session.add(new_post)
        db.session.commit()
        # Re-read so that timestamp is populated
        db.session.refresh(new_post)

        return jsonify({
            "message": "Post creado",
            "post": serialize_post(new_post)
        }), 201

    # GET: only root-level posts
    posts = Post.query.filter_by(parent_id=None).order_by(Post.timestamp.desc()).all()
    return jsonify([serialize_post(p) for p in posts]), 200

@app.route('/api/vote', methods=['POST'])
def api_vote():
    if 'user_id' not in session:
        return jsonify({"error": "No autenticado"}), 401
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Datos inválidos"}), 400

    post_id = data.get('post_id')
    vote_type = data.get('vote_type')

    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post no encontrado"}), 404

    if vote_type == 'up':
        post.upvotes += 1
    elif vote_type == 'down':
        post.downvotes += 1
    else:
        return jsonify({"error": "Tipo de voto inválido"}), 400

    db.session.commit()
    return jsonify({"message": "Voto registrado", "upvotes": post.upvotes, "downvotes": post.downvotes}), 200

# ─── Static fallback (must be last) ───

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
