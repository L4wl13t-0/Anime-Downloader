
# API Reference (Users)

## `POST /api/users` | Registro de nuevo usuario

```js
//BODY REQUEST JSON

{
  "username": "test",
  "password": "1234",
  "email": "test@gmail.com"
}
```

## `GET /api/users` | Inicio de sesion de usuario

```js
//HEADER AUTHORIZATION | BASIC AUTH
```

| Parameter         | Type      | Description       |
| :---------------- | :-------- | :---------------- |
| `username`        | `string`  | Basic Auth        |  
| `passwword`       | `string`  | Basic Auth        |
| `stay_loged_in`   | `boolean` | Params            |

## `DELETE /api/users/<user>` | Eliminación de un usuario

| Parameter         | Type      | Description       |
| :---------------- | :-------- | :---------------- |
| `Bearer Token`        | `token`  | Authorization Header       |  
| `<user>`       | `id`  | URL Parameter        |

## `PUT /api/users` | Actualizacion del propio usuario

| Parameter         | Type      | Description       |
| :---------------- | :-------- | :---------------- |
| `Bearer Token`        | `token`  | Authorization Header       |  

```js
//BODY REQUEST JSON

{
  "data": {
    "username": "test",
    "password": "1234",
    "email": "test@gmail.com"
  }
}
```

## `PUT /api/users/<user>` | Actualización Privilegiada de usuario

| Parameter         | Type      | Description       |
| :---------------- | :-------- | :---------------- |
| `Bearer Token`        | `token`  | Authorization Header       |
| `<user>`        | `id`  | URL Parameter       |  

```js
//BODY REQUEST JSON

{
  "data": {
    "username": "test",
    "password": "1234",
    "email": "test@gmail.com"
  }
}
```

## `GET /api/users/profile` | Obtención del perfil propio

| Parameter         | Type      | Description       |
| :---------------- | :-------- | :---------------- |
| `Bearer Token`        | `token`  | Authorization Header       |

## `GET /api/users/<username>` | Obtención del perfil de un usuario

| Parameter         | Type      | Description       |
| :---------------- | :-------- | :---------------- |
| `<username>`        | `string`  | URL Parameter   |
