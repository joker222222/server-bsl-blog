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
    "message": "Пользователь успешно создан.",
    "user_id": "integer"
  }
  ```
- **400 Bad Request**
  ```json
  {
    "error": "Имя пользователя и пароль обязательны."
  }
  ```
- **409 Conflict**
  ```json
  {
    "error": "Пользователь уже существует."
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
    "message": "Вход выполнен успешно.",
    "token": "string"
  }
  ```
- **400 Bad Request**
  ```json
  {
    "error": "Имя пользователя и пароль обязательны."
  }
  ```
- **401 Unauthorized**
  ```json
  {
    "error": "Неверные учетные данные."
  }
  ```

### 3. Выход пользователя

**POST** `/logout`

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "Выход выполнен успешно."
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
    "message": "Пользователь успешно удален."
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "Пользователь не найден."
  }
  ```
- **403 Forbidden**
  ```json
  {
    "error": "Вы можете удалить только свою учетную запись."
  }
  ```
- **401 Unauthorized**
  ```json
  {
    "error": "Неверный токен."
  }
  ```

### 5. Получить все посты

**GET** `/posts`

**Заголовки:**

```
Authorization: <JWT Token>
```

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

**Заголовки:**

```
Authorization: <JWT Token>
```

**Ответы:**

- **200 OK**
  ```json
  {
    "id": "integer",
    "title": "string",
    "content": "string",
    "created_at": "ISO 8601 datetime",
    "user_id": "integer"
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "Пост не найден."
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
  "title": "string (max: 255 символов)",
  "content": "string (max: 5000 символов)"
}
```

**Ответы:**

- **201 Created**
  ```json
  {
    "message": "Пост успешно создан.",
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
    "error": "Заголовок и контент обязательны и должны соответствовать ограничениям по количеству символов."
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
  "title": "string (необязательно)",
  "content": "string (необязательно)"
}
```

**Ответы:**

- **200 OK**
  ```json
  {
    "message": "Пост успешно обновлен."
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "Пост не найден."
  }
  ```
- **403 Forbidden**
  ```json
  {
    "error": "Вы можете редактировать только свои посты."
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
    "message": "Пост успешно удален."
  }
  ```
- **404 Not Found**
  ```json
  {
    "error": "Пост не найден."
  }
  ```
- **403 Forbidden**
  ```json
  {
    "error": "Вы можете удалять только свои посты."
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
