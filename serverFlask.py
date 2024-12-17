from flask import Flask, request, jsonify, abort, session as flask_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

app = Flask(__name__)
app.secret_key = "zhulikiettttta"  # Для управления сессиями

# Инициализация базы данных
DATABASE_URL = "sqlite:///blog.db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

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

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title}, user_id={self.user_id})>"

# --- API Роуты ---

# 1. Создание пользователя
@app.route('/users', methods=['POST'])
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
    return jsonify({"message": "User created successfully.", "user_id": new_user.id}), 201

# 2. Авторизация пользователя
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        abort(400, description="Username and password are required.")

    username = data['username']
    password = data['password']
    user = session.query(User).filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"error": "Invalid credentials."}), 401
    
    flask_session['user_id'] = user.id
    return jsonify({"message": "Login successful.", "user_id": user.id}), 200

# 3. Выход из аккаунта пользователя
@app.route('/logout', methods=['POST'])
def logout():
    flask_session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully."}), 200

# 4. Удаление пользователя
@app.route('/users/<string:username>', methods=['DELETE'])
def delete_user(username):
    if 'user_id' not in flask_session:
        return jsonify({"error": "Unauthorized."}), 401

    user = session.query(User).filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    if flask_session['user_id'] != user.id:
        return jsonify({"error": "You can only delete your own account."}), 403

    session.delete(user)
    session.commit()
    return jsonify({"message": "User deleted successfully."}), 200

# 5. Получение всех постов
@app.route('/posts', methods=['GET'])
def get_all_posts():
    posts = session.query(Post).all()
    return jsonify([
        {"id": post.id, "title": post.title, "content": post.content, "created_at": post.created_at.isoformat(), "user_id": post.user_id}
        for post in posts
    ]), 200

# 6. Получение одного поста
@app.route('/posts/<int:post_id>', methods=['GET'])
def get_single_post(post_id):
    post = session.query(Post).filter_by(id=post_id).first()
    if not post:
        return jsonify({"error": "Post not found."}), 404
    return jsonify({
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at.isoformat(),
        "user_id": post.user_id
    }), 200

# 7. Изменение поста
@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    if 'user_id' not in flask_session:
        return jsonify({"error": "Unauthorized."}), 401

    post = session.query(Post).filter_by(id=post_id).first()
    if not post:
        return jsonify({"error": "Post not found."}), 404

    if post.user_id != flask_session['user_id']:
        return jsonify({"error": "You can only edit your own posts."}), 403

    data = request.json
    if 'title' in data:
        post.title = data['title']
    if 'content' in data:
        post.content = data['content']

    session.commit()
    return jsonify({"message": "Post updated successfully."}), 200

# 8. Создание нового поста
@app.route('/posts', methods=['POST'])
def create_post():
    data = request.json
    if not data or 'title' not in data or 'content' not in data or 'username' not in data:
        abort(400, description="Title, content, and username are required.")

    title = data['title']
    content = data['content']
    username = data['username']

    # Проверка, существует ли пользователь
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    # Создание нового поста
    new_post = Post(title=title, content=content, author=user)
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

# Запуск приложения
if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(debug=True)
