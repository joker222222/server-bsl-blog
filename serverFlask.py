from flask import Flask, request, jsonify, abort, session as flask_session
from flask_cors import CORS, cross_origin
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timedelta, timezone
import jwt
from functools import wraps

app = Flask(__name__)
app.secret_key = "zhulikiettttta"  # Для управления сессиями
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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

# Определение моделей User и Post
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
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
@app.route('/users', methods=['POST'])
@cross_origin()
def create_user():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        abort(400, description="Username and password are required.")
    username = data['username']
    password = data['password']

    if session.query(User).filter_by(username=username).first():
        return jsonify({"error": "User already exists."}), 409

    new_user = User(username=username, password=password)
    session.add(new_user)
    session.commit()
    return jsonify({"message": "User created successfully."}), 201  # , "user_id": new_user.id

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

    return jsonify({"message": "Login successful.", "token": token}), 200

# 3. Выход из аккаунта пользователя
@app.route('/logout', methods=['POST'])
@cross_origin()
def logout():
    flask_session.pop('user_id', None)
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
def get_single_post(post_id):
    post = session.query(Post).filter_by(id=post_id).first()
    if not post:
        return jsonify({"error": "Post not found."}), 404
    post.views += 1
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
@app.route('/token', methods=['POST'])
@cross_origin()
@token_required
def validation_token():
    token_data = jwt.decode(request.headers.get('Authorization'), JWT_SECRET, algorithms=[JWT_ALGORITHM])
    user = session.query(User).filter_by(id=token_data['user_id']).first()
    if not user:
        return jsonify({"error": "Invalid token."}), 404
    return jsonify({"message": "Valid token", "user_id": user.username}), 200

# 11. Получение данных о пользователе (все его посты)
@app.route('/user/<string:user_id>', methods=['GET'])
@cross_origin()
def get_user_posts(user_id):

    # Проверяем, что запрашиваемый пользователь существует
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    # Получаем все посты пользователя
    posts = session.query(Post).filter_by(user_id=user.id).all()

    # Формируем ответ с постами пользователя
    return jsonify([
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at.isoformat(),
            "views": post.views
        } for post in posts
    ]), 200

# Запуск приложения
if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(host="0.0.0.0", port=5000, debug=True)