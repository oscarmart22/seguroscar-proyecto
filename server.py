import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)

db_url = os.getenv('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

ADMIN_USERNAME = 'oscarmart22'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ─── Models ───

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    replies = db.relationship(
        'Post',
        backref=db.backref('parent', remote_side=[id]),
        lazy=True,
        order_by='Post.timestamp.asc()'
    )

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)  # 1 = upvote, -1 = downvote

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_vote'),)

# ─── DB Init ───

with app.app_context():
    db.create_all()
    print("[INIT] Base de datos lista.")

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return send_from_directory('.', 'index.html')

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

    login_user(new_user, remember=True)
    return jsonify({"message": "Usuario registrado exitosamente", "username": new_user.username}), 201

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return send_from_directory('.', 'index.html')

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
        login_user(user, remember=True)
        return jsonify({"message": "Inicio de sesión exitoso", "username": user.username}), 200

    return jsonify({"error": "Credenciales inválidas"}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Sesión cerrada"}), 200

@app.route('/api/me', methods=['GET'])
def get_me():
    if current_user.is_authenticated:
        return jsonify({"logged_in": True, "username": current_user.username})
    return jsonify({"logged_in": False})

@app.route('/foro')
def foro():
    return send_from_directory('.', 'foro.html')

# ─── Forum API ───

def get_vote_score(post_id):
    from sqlalchemy import func
    result = db.session.query(func.coalesce(func.sum(Vote.value), 0)).filter_by(post_id=post_id).scalar()
    return int(result)

def serialize_post(post, current_user_id=None):
    autor = post.user.username if post.user else 'Usuario Anónimo'
    is_admin = (autor == ADMIN_USERNAME)
    score = get_vote_score(post.id)

    # Current user's vote on this post
    user_vote = 0
    if current_user_id:
        existing = Vote.query.filter_by(user_id=current_user_id, post_id=post.id).first()
        if existing:
            user_vote = existing.value

    return {
        "id": post.id,
        "username": autor,
        "is_admin": is_admin,
        "content": post.content,
        "timestamp": post.timestamp.strftime("%Y-%m-%d %H:%M:%S") if post.timestamp else "",
        "score": score,
        "user_vote": user_vote,
        "parent_id": post.parent_id,
        "replies": [serialize_post(reply, current_user_id) for reply in (post.replies or [])]
    }

@app.route('/api/posts', methods=['GET', 'POST'])
def api_posts():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return jsonify({"error": "No autenticado"}), 401

        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({"error": "Datos inválidos"}), 400

        content = data.get('content', '').strip() if data else ''
        parent_id = data.get('parent_id') if data else None

        if not content:
            return jsonify({"error": "El contenido no puede estar vacío"}), 400

        new_post = Post(user_id=current_user.id, content=content, parent_id=parent_id)
        db.session.add(new_post)
        db.session.commit()
        db.session.refresh(new_post)

        return jsonify({
            "message": "Post creado",
            "post": serialize_post(new_post, current_user.id)
        }), 201

    # GET
    current_uid = current_user.id if current_user.is_authenticated else None
    posts = Post.query.filter_by(parent_id=None).order_by(Post.timestamp.desc()).all()
    return jsonify([serialize_post(p, current_uid) for p in posts]), 200

@app.route('/api/vote', methods=['POST'])
def api_vote():
    if not current_user.is_authenticated:
        return jsonify({"error": "No autenticado"}), 401
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Datos inválidos"}), 400

    post_id = data.get('post_id')
    vote_type = data.get('vote_type')

    if vote_type not in ('up', 'down'):
        return jsonify({"error": "Tipo de voto inválido"}), 400

    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post no encontrado"}), 404

    new_value = 1 if vote_type == 'up' else -1
    user_id = current_user.id

    existing_vote = Vote.query.filter_by(user_id=user_id, post_id=post_id).first()

    if existing_vote:
        if existing_vote.value == new_value:
            # Same button pressed again → remove vote (toggle off)
            db.session.delete(existing_vote)
            db.session.commit()
            return jsonify({
                "message": "Voto eliminado",
                "score": get_vote_score(post_id),
                "user_vote": 0
            }), 200
        else:
            # Switch vote direction
            existing_vote.value = new_value
            db.session.commit()
            return jsonify({
                "message": "Voto actualizado",
                "score": get_vote_score(post_id),
                "user_vote": new_value
            }), 200
    else:
        # New vote
        new_vote = Vote(user_id=user_id, post_id=post_id, value=new_value)
        db.session.add(new_vote)
        db.session.commit()
        return jsonify({
            "message": "Voto registrado",
            "score": get_vote_score(post_id),
            "user_vote": new_value
        }), 200

# ─── Static fallback (must be last) ───

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
