# API Documentation for Blog Platform

## Base URL

```
http://<your_host>:5000
```

## Endpoints

### 1. Создание пользователя

**POST** `/signup`

**Тело запроса:**

```json
{
  "username": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "avatar": "file.png.jpg"
}
```

**Ответы:**

- **201 Created**
  ```json
  {
    "message": "User created successfully."
  }
  ```
- **400 Bad Request**
  ```json
  {
    "error": "Username and password are required."
  }
  ```
- **409 Conflict**
  ```json
  {
    "error": "User already exists."
  }
  ```

### 2. Авторизация пользователя

**POST** `/login`

**Тело запроса:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "Login successful.",
    "token": "string",
    "avatar": "file_path_string.jpg"
  }
  ```
- **400 Bad Request**
  ```json
  {
    "error": "Username and password are required."
  }
  ```
- **401 Unauthorized**
  ```json
  {
    "error": "Invalid credentials."
  }
  ```

### 3. Выход из аккаунта пользователя

**POST** `/logout`

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "Logged out successfully."
  }
  ```

### 4. Удаление пользователя

**DELETE** `/users/<string:username>`

**Тело запроса:** Не требуется.

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "User deleted successfully."
  }
  ```
- **403 Forbidden**
  ```json
  {
    "error": "You can only delete your own account."
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "User not found."
  }
  ```

### 5. Получение всех постов

**GET** `/posts`

**Ответы:**

- **200 OK**
  ```json
  [
    {
      "id": "integer",
      "title": "string",
      "content": "string",
      "created_at": "string",
      "user_id": "string"
    }
  ]
  ```

### 6. Получение одного поста

**GET** `/posts/<int:post_id>`

**Ответы:**

- **200 OK**
  ```json
  {
    "id": "integer",
    "title": "string",
    "content": "string",
    "created_at": "string",
    "user_id": "string",
    "views": "integer"
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "Post not found."
  }
  ```

### 7. Создание нового поста

**POST** `/posts`

**Тело запроса:**

```json
{
  "title": "string",
  "content": "string"
}
```

**Ответы:**

- **201 Created**
  ```json
  {
    "message": "Post created successfully.",
    "post_id": "integer",
    "title": "string",
    "content": "string",
    "created_at": "string",
    "user_id": "integer"
  }
  ```
- **400 Bad Request**
  ```json
  {
    "error": "Title and content are required."
  }
  ```

### 8. Изменение поста

**PUT** `/posts/<int:post_id>`

**Тело запроса:**

```json
{
  "title": "string",
  "content": "string"
}
```

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "Post updated successfully."
  }
  ```
- **403 Forbidden**
  ```json
  {
    "error": "You can only edit your own posts."
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "Post not found."
  }
  ```

### 9. Удаление поста

**DELETE** `/posts/<int:post_id>`

**Тело запроса:** Не требуется.

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "Post deleted successfully."
  }
  ```
- **403 Forbidden**
  ```json
  {
    "error": "You can only delete your own posts."
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "Post not found."
  }
  ```

### 10. Валидация токена

**POST** `/token/check`

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "Valid token",
    "user_id": "string"
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "Invalid token."
  }
  ```

### 11. Получение данных о постах пользователя

**GET** `/author/<string:user_id>/posts`

**Ответы:**

- **200 OK**
  ```json
  {
    "all_views": "integer",
    "posts": [
      {
        "id": "integer",
        "title": "string",
        "content": "string",
        "created_at": "string",
        "views": "integer"
      }
    ]
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "User not found."
  }
  ```

### 12. Получение данных пользователя

**GET** `/author/<string:user_id>/posts`

**Ответы:**

- **200 OK**
  ```json
  {
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "avatar": "file_path_string.jpg",
    "all_posts": "string"
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "User not found."
  }
  ```

### 13. Получение аватара пользователя

**GET** `/avatars/<path:filename>`

**Ответы:**

- **200 OK**
  ```json
  {
    "img_file"
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "User not found."
  }
  ```

## Авторизация

Для работы с защищёнными эндпоинтами (создание постов, изменение и удаление постов, удаление пользователей, валидация токена), необходимо передавать токен в заголовке `Authorization`:

```plaintext
Authorization: <your_token>
```

## Коды ошибок

- **400 Bad Request**: Отсутствуют или неверные данные в запросе.
- **401 Unauthorized**: Токен отсутствует, недействителен или истек.
- **403 Forbidden**: Пользователь не авторизован для выполнения действия.
- **404 Not Found**: Ресурс не найден.
- **409 Conflict**: Ресурс уже существует.

## Примечания

- Все эндпоинты, требующие аутентификации, должны содержать заголовок `Authorization` с действительным токеном JWT.
- Даты возвращаются в формате ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`).
