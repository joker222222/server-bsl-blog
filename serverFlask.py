from flask import Flask, request, jsonify, abort, session as flask_session
from flask import send_file
from flask_cors import CORS, cross_origin
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timedelta, timezone
import jwt
from functools import wraps
import os
import secrets
import base64

app = Flask(__name__)
app.secret_key = "zhulikiettttta"  # Для управления сессиями
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = 'img_avatar'

JWT_SECRET = "blog_platform_mega_super_style_shhhet"
JWT_ALGORITHM = "HS256"

# Инициализация базы данных
DATABASE_URL = "sqlite:///blog.db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Утилита для проверки JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing."}), 401
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": True})
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token."}), 401
        return f(*args, **kwargs)
    return decorated

# Утилита для создания пути к файлу
def generate_avatar_path(extension='jpg'):
    # Генерируем случайную строку для имени файла
    random_filename = secrets.token_hex(16) + '.' + extension
    
    # Указываем путь к папке img_avatar
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], random_filename)
    avatar_path = random_filename
    return save_path, avatar_path

# Определение моделей User и Post
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    avatar = Column(String(20), nullable=False)
    posts = relationship('Post', back_populates='author', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    author = relationship('User', back_populates='posts')
    views = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title}, user_id={self.user_id})>"

# --- API Роуты ---

# 1. Создание пользователя
@app.route('/signup', methods=['POST'])
@cross_origin()
def create_user():
    if 'username' not in request.form or 'password' not in request.form or \
       'first_name' not in request.form or 'last_name' not in request.form:
        abort(400, description="Username and password are required.")
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']

    try:
        binary_data_avatar = request.files['avatar'].read()
        save_path, avatar_path = generate_avatar_path()

        def save_binary_file(binary_data, filepath):
            # Открываем файл для записи в бинарном режиме ('wb')
            with open(filepath, 'wb') as file:
                file.write(binary_data)
        save_binary_file(binary_data_avatar, save_path)
    except:
        pass

    if session.query(User).filter_by(username=username).first():
        return jsonify({"error": "User already exists."}), 409

    new_user = User(username=username, password=password, first_name=first_name, last_name=last_name, avatar=avatar_path)
    session.add(new_user)
    session.commit()
    return jsonify({"message": "User created successfully."}), 201 

# 2. Авторизация пользователя
@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        abort(400, description="Username and password are required.")

    username = data['username']
    password = data['password']
    user = session.query(User).filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"error": "Invalid credentials."}), 401
    
    token_lifetime = timedelta(hours=1)
    expiration_time = datetime.now(timezone.utc) + token_lifetime

    # Генерация JWT токена с временем жизни
    payload = {
        "user_id": user.id, 
        "username": user.username,
        "exp": expiration_time  # Устанавливаем время жизни токена
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Декодирование токена для преобразования в строку (если нужно)
    token = token.decode('utf-8') if isinstance(token, bytes) else token

    return jsonify({"message": "Login successful.", "token": token, "avatar": user.avatar}), 200

# 3. Выход из аккаунта пользователя
@app.route('/logout', methods=['POST'])
@cross_origin()
@token_required
def logout():
    token_data = jwt.decode(request.headers.get('Authorization'), JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    flask_session.pop(token_data['user_id'], None)
    return jsonify({"message": "Logged out successfully."}), 200

# 4. Удаление пользователя
@app.route('/users/<string:username>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_user(username):
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    token_data = jwt.decode(request.headers.get('Authorization'), JWT_SECRET, algorithms=[JWT_ALGORITHM])
    if token_data['user_id'] != user.id:
        return jsonify({"error": "You can only delete your own account."}), 403

    session.delete(user)
    session.commit()
    return jsonify({"message": "User deleted successfully."}), 200

# 5. Получение всех постов
@app.route('/posts', methods=['GET'])
@cross_origin()
def get_all_posts():
    posts = session.query(Post).all()
    return jsonify([
        {"id": post.id, 
        "title": post.title, 
        "content": post.content, 
        "created_at": post.created_at.isoformat(), 
        "user_id": post.author.username}
        for post in posts
    ]), 200

# 6. Получение одного поста
@app.route('/posts/<int:post_id>', methods=['GET'])
@cross_origin()
def get_single_post(post_id):
    post = session.query(Post).filter_by(id=post_id).first()
    if not post:
        return jsonify({"error": "Post not found."}), 404
    post.views += 1
    session.commit()
    return jsonify({
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at.isoformat(),
        "user_id": post.author.username,
        "views": post.views
    }), 200

# 7. Создание нового поста
@app.route('/posts', methods=['POST'])
@cross_origin()
@token_required
def create_post():
    data = request.json
    if not data or 'title' not in data or 'content' not in data:
        abort(400, description="Title and content are required.")

    token_data = jwt.decode(request.headers.get('Authorization'), JWT_SECRET, algorithms=[JWT_ALGORITHM])
    user = session.query(User).filter_by(id=token_data['user_id']).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    new_post = Post(title=data['title'], content=data['content'], author=user, views=0)
    session.add(new_post)
    session.commit()

    return jsonify({
        "message": "Post created successfully.",
        "post_id": new_post.id,
        "title": new_post.title,
        "content": new_post.content,
        "created_at": new_post.created_at.isoformat(),
        "user_id": new_post.user_id
    }), 201

# 8. Изменение поста
@app.route('/posts/<int:post_id>', methods=['PUT'])
@cross_origin()
@token_required
def update_post(post_id):
    token_data = jwt.decode(request.headers.get('Authorization'), JWT_SECRET, algorithms=[JWT_ALGORITHM])

    post = session.query(Post).filter_by(id=post_id).first()
    if not post:
        return jsonify({"error": "Post not found."}), 404

    if post.user_id != token_data['user_id']:
        return jsonify({"error": "You can only edit your own posts."}), 403

    data = request.json
    if 'title' in data:
        post.title = data['title']
    if 'content' in data:
        post.content = data['content']

    session.commit()
    return jsonify({"message": "Post updated successfully."}), 200

# 9. Удаление поста
@app.route('/posts/<int:post_id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_post(post_id):
    # Распаковываем токен
    token_data = jwt.decode(request.headers.get('Authorization'), JWT_SECRET, algorithms=[JWT_ALGORITHM])

    # Ищем пост
    post = session.query(Post).filter_by(id=post_id).first()
    if not post:
        return jsonify({"error": "Post not found."}), 404

    # Проверяем, принадлежит ли пост текущему пользователю
    if post.user_id != token_data['user_id']:
        return jsonify({"error": "You can only delete your own posts."}), 403

    # Удаляем пост
    session.delete(post)
    session.commit()

    return jsonify({"message": "Post deleted successfully."}), 200

# 10. Валидация токена
@app.route('/token/check', methods=['POST'])
@cross_origin()
@token_required
def validation_token():
    token_data = jwt.decode(request.headers.get('Authorization'), JWT_SECRET, algorithms=[JWT_ALGORITHM])
    user = session.query(User).filter_by(id=token_data['user_id']).first()
    if not user:
        return jsonify({"error": "Invalid token."}), 404
    return jsonify({"message": "Valid token", "user_id": user.username}), 200

# 11. Получение данных о постах пользователя
@app.route('/author/<string:user_id>/posts', methods=['GET'])
@cross_origin()
def get_user_posts(user_id):

    # Проверяем, что запрашиваемый пользователь существует
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    # Получаем все посты пользователя
    posts = session.query(Post).filter_by(user_id=user.id).all()
    all_views = 0
    posts = []
    for post in posts:
        posts.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at.isoformat(),
            "views": post.views
        })
        all_views += post.views
    # Формируем ответ с постами пользователя
    return jsonify({
        "all_views": all_views,
        "posts": posts
    }), 200

# 12. Получение данных пользователя
@app.route('/author/<string:user_id>', methods=['GET'])
@cross_origin()
def get_user_info(user_id):

    # Проверяем, что запрашиваемый пользователь существует
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    all_posts = len(session.query(Post).filter_by(user_id=user.id).all())
    return jsonify({
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar": user.avatar,
        "all_posts": all_posts
    }), 200

# 13. Получение Аватара пользователя  
@app.route('/avatars/<path:filename>', methods=['GET'])
@cross_origin()
def get_avatar(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Avatar not found."}), 404
    return send_file(file_path)

# Запуск приложения
if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(host="0.0.0.0", port=5000, debug=True)