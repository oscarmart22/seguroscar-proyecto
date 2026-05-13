import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory, abort, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)

db_url = os.getenv('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

@app.after_request
def set_csrf_cookie(response):
    response.set_cookie('csrf_token', generate_csrf(), samesite='Lax')
    return response

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ─── Forms ───
class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2, max=80)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir')])

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

# ─── Models ───

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

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



# ─── DB Init ───

with app.app_context():
    try:
        db.create_all()
        print("[INIT] Base de datos lista.")
    except Exception as e:
        print(f"[INIT] Error o tablas ya existentes: {e}")

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
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('index.html', form=form)

    # For AJAX JSON compatibility with Flask-WTF
    if request.is_json:
        form = RegistrationForm(data=request.get_json())
    
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "El usuario ya existe"}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password, is_admin=False)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user, remember=True)
        return jsonify({"message": "Usuario registrado exitosamente", "username": new_user.username, "is_admin": new_user.is_admin}), 201
    
    if request.method == 'POST':
        # Collect validation errors
        errors = []
        for field, messages in form.errors.items():
            field_label = getattr(form, field).label.text
            errors.append(f"{field_label}: {', '.join(messages)}")
        return jsonify({"error": ". ".join(errors)}), 400

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('index.html', form=form)

    if request.is_json:
        form = LoginForm(data=request.get_json())

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return jsonify({"message": "Inicio de sesión exitoso", "username": user.username, "is_admin": user.is_admin}), 200

        return jsonify({"error": "Credenciales inválidas"}), 401
    
    return jsonify({"error": "Datos inválidos"}), 400

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Sesión cerrada"}), 200

@app.route('/api/me', methods=['GET'])
def get_me():
    if current_user.is_authenticated:
        return jsonify({"logged_in": True, "username": current_user.username, "is_admin": current_user.is_admin})
    return jsonify({"logged_in": False})

@app.route('/foro')
def foro():
    return render_template('foro.html')

# ─── Forum API ───

def serialize_post(post, current_user_id=None):
    autor = post.user.username if post.user else 'Usuario Anónimo'
    is_admin = post.user.is_admin if post.user else False

    return {
        "id": post.id,
        "username": autor,
        "is_admin": is_admin,
        "content": post.content,
        "timestamp": post.timestamp.strftime("%Y-%m-%d %H:%M:%S") if post.timestamp else "",
        "parent_id": post.parent_id,
        "replies": [serialize_post(reply, current_user_id) for reply in (post.replies or [])]
    }

@app.route('/api/posts', methods=['GET', 'POST'])
def api_posts():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return jsonify({"error": "No autenticado"}), 401

        # Rate limiting for posting: 20 per hour
        @limiter.limit("20 per hour")
        def limit_posts():
            pass
        
        try:
            limit_posts()
        except Exception:
            return jsonify({"error": "Límite de publicaciones excedido (20 por hora)"}), 429

        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({"error": "Datos inválidos"}), 400

        content = data.get('content', '').strip() if data else ''
        parent_id = data.get('parent_id') if data else None

        if not content:
            return jsonify({"error": "El contenido no puede estar vacío"}), 400

        if len(content) > 500:
            return jsonify({"error": "El contenido no puede exceder los 500 caracteres"}), 400

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

@app.route('/api/posts/delete/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post no encontrado"}), 404

    if post.user != current_user and not current_user.is_admin:
        abort(403)

    def delete_recursive(p):
        for child in p.replies:
            delete_recursive(child)
        db.session.delete(p)

    delete_recursive(post)
    db.session.commit()
    return jsonify({"message": "Post eliminado exitosamente"}), 200

@app.route('/api/posts/edit/<int:post_id>', methods=['PUT'])
@login_required
def edit_post(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post no encontrado"}), 404

    if post.user != current_user:
        abort(403)

    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Datos inválidos"}), 400

    new_content = data.get('content', '').strip()
    if not new_content:
        return jsonify({"error": "El contenido no puede estar vacío"}), 400

    post.content = new_content
    db.session.commit()
    return jsonify({"message": "Post actualizado", "post": serialize_post(post, current_user.id)}), 200

# ─── Static fallback (must be last) ───

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
