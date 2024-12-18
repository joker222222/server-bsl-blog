# API Documentation for Blog Platform

## Base URL

```
http://<your_host>:5000
```

## Endpoints

### 1. Создание пользователя

**POST** `/users`

**Тело запроса:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Ответы:**

- **201 Created**
  ```json
  {
    "message": "User created successfully.",
    "user_id": "integer"
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

### 2. Вход пользователя

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
    "token": "string"
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

### 3. Выход пользователя

**POST** `/logout`

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "Logged out successfully."
  }
  ```

### 4. Удаление пользователя

**DELETE** `/users/{username}`

**Заголовки:**

```
Authorization: <JWT Token>
```

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "User deleted successfully."
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "User not found."
  }
  ```
- **403 Forbidden**
  ```json
  {
    "error": "You can only delete your own account."
  }
  ```
- **401 Unauthorized**
  ```json
  {
    "error": "Invalid token."
  }
  ```

### 5. Получить все посты

**GET** `/posts`

**Ответы:**

- **200 OK**
  ```json
  [
    {
      "id": "integer",
      "title": "string",
      "content": "string",
      "created_at": "ISO 8601 datetime",
      "user_id": "integer"
    }
  ]
  ```

### 6. Получить один пост

**GET** `/posts/{post_id}`

**Ответы:**

- **200 OK**
  ```json
  {
    "id": "integer",
    "title": "string",
    "content": "string",
    "created_at": "ISO 8601 datetime",
    "user_id": "integer",
    "views": "integer"
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "Post not found."
  }
  ```

### 7. Создание поста

**POST** `/posts`

**Заголовки:**

```
Authorization: <JWT Token>
```

**Тело запроса:**

```json
{
  "title": "string (max: 255 characters)",
  "content": "string (max: 5000 characters)"
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
    "created_at": "ISO 8601 datetime",
    "user_id": "integer"
  }
  ```
- **400 Bad Request**
  ```json
  {
    "error": "Title and content are required, and must adhere to character limits."
  }
  ```

### 8. Обновление поста

**PUT** `/posts/{post_id}`

**Заголовки:**

```
Authorization: <JWT Token>
```

**Тело запроса:**

```json
{
  "title": "string (optional)",
  "content": "string (optional)"
}
```

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "Post updated successfully."
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "Post not found."
  }
  ```
- **403 Forbidden**
  ```json
  {
    "error": "You can only edit your own posts."
  }
  ```

### 9. Удаление поста

**DELETE** `/posts/{post_id}`

**Заголовки:**

```
Authorization: <JWT Token>
```

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "Post deleted successfully."
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "Post not found."
  }
  ```
- **403 Forbidden**
  ```json
  {
    "error": "You can only delete your own posts."
  }
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
