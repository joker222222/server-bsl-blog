# 1. Создание пользователя
  URL: /users
  Метод: POST
  Описание: Создает нового пользователя.

  Тело запроса (JSON):
  json
  {
    "username": "example_user",
    "password": "example_password"
  }

  Ответы:
  201 Created:
  json
  {
    "message": "User created successfully.",
    "user_id": 1
  }

  400 Bad Request:
  Если username или password не переданы:
  json
  {
    "description": "Username and password are required."
  }

  409 Conflict:
  Если пользователь с таким именем уже существует:
  json
  {
    "error": "User already exists."
  }

# 2. Авторизация пользователя
  URL: /login
  Метод: POST
  Описание: Выполняет вход пользователя в систему.

  Тело запроса (JSON):
  json
  {
    "username": "example_user",
    "password": "example_password"
  }

  Ответы:
  200 OK:
  json
  {
    "message": "Login successful.",
    "user_id": 1
  }

  400 Bad Request:
  Если username или password не переданы:
  json
  {
    "description": "Username and password are required."
  }

  401 Unauthorized:
  Если учетные данные неверные:
  json
  {
    "error": "Invalid credentials."
  }

# 4. Удаление пользователя
  URL: /users/<username>
  Метод: DELETE
  Описание: Удаляет пользователя с указанным именем (можно удалить только свой аккаунт).

  Параметры URL:
  <username>: Имя пользователя, которого нужно удалить.
  Ответы:
  200 OK:
  json
  {
    "message": "User deleted successfully."
  }

  401 Unauthorized:
  Если пользователь не авторизован:
  json
  {
    "error": "Unauthorized."
  }

  404 Not Found:
  Если пользователь не найден:
  json
  {
    "error": "User not found."
  }

  403 Forbidden:
  Если пользователь пытается удалить чужой аккаунт:
  json
  {
    "error": "You can only delete your own account."
  }

 # 5. Получение всех постов
  URL: /posts
  Метод: GET
  Описание: Возвращает список всех постов.

  Ответы:
  200 OK:
  json
  [
    {
      "id": 1,
      "title": "First Post",
      "content": "This is my first post.",
      "created_at": "2024-12-17T10:00:00Z",
      "user_id": 1
    }
    ,
    {
      "id": 2,
      "title": "Second Post",
      "content": "Another post content.",
      "created_at": "2024-12-17T11:00:00Z",
      "user_id": 2
    }

  ]

# 6. Получение одного поста
  URL: /posts/<post_id>
  Метод: GET
  Описание: Возвращает данные поста по его ID.

  Параметры URL:
  <post_id>: ID поста.
  Ответы:
  200 OK:
  json
  {
    "id": 1,
    "title": "First Post",
    "content": "This is my first post.",
    "created_at": "2024-12-17T10:00:00Z",
    "user_id": 1
  }

  404 Not Found:
  Если пост с указанным ID не найден:
  json
  {
    "error": "Post not found."
  }


# 7. Создание нового поста
  URL: /posts
  Метод: POST
  Описание: Создает новый пост, связанный с пользователем. Для создания поста необходимо передать данные о пользователе и посте.

  Тело запроса (JSON):
  json
  {
    "title": "My New Post",
    "content": "This is the content of my new post.",
    "username": "example_user"
  }

  Ответы:
  201 Created: Если пост успешно создан:
  json
  {
    "message": "Post created successfully.",
    "post_id": 1,
    "title": "My New Post",
    "content": "This is the content of my new post.",
    "created_at": "2024-12-17T12:00:00Z",
    "user_id": 1
  }

  400 Bad Request:
  Если не переданы обязательные поля title, content или username:
  json
  {
    "description": "Title, content, and username are required."
  }

  404 Not Found:
  Если пользователь с указанным именем не найден:
  json
  {
    "error": "User not found."
  }


# 8. Изменение поста
  URL: /posts/<post_id>
  Метод: PUT
  Описание: Изменяет данные существующего поста (можно редактировать только свои посты).

  Параметры URL:
  <post_id>: ID поста.
  Тело запроса (JSON):
  json
  {
    "title": "Updated Title",
    "content": "Updated content of the post."
  }

  Ответы:
  200 OK:
  json
  {
    "message": "Post updated successfully."
  }

  401 Unauthorized:
  Если пользователь не авторизован:
  json
  {
    "error": "Unauthorized."
  }

  404 Not Found:
  Если пост с указанным ID не найден:
  json
  {
    "error": "Post not found."
  }

  403 Forbidden:
  Если пользователь пытается редактировать чужой пост:
  json
  {
    "error": "You can only edit your own posts."
  }
