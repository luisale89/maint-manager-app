# API v1 endpoints

`** http errors and JSON responses**`
* *url not found* -> `http code: 404`
```json
    {
        "data": {},
        "message": "msg...",
        "result": "error"
    }
```

* *internal server error* -> `http code: 500`
```json
    {
        "data": {},
        "message": "msg...",
        "result": "error"
    }
```

* *bad request* -> `http code: 400`
```json
    {
        "data": {},
        "message": "msg...",
        "result": "error"
    }
```


---
`** auth endpoints **`
---


## `GET` **email-query**

    endpoint para consultar la existencia de un email en la app

* *url*
    ```http
    GET /api/v1/auth/email-query?email="valid@email"
    ```

    | Parameter | Type | Description | Required
    | :--- | :--- | :--- | :---
    | `email` | `string` | query email | `True`

* *headers*
    ```json
    {
        "content-type":"application/json"
    }
    ```

* *JSON responses*
    - *email found* -> `http code: 200`
    ```json
    {
        "data": {},
        "message": "msg...",
        "result": "success"
    }
    ```
    - *email not found* -> `http code: 404`
    ```json
    {
        "data": {},
        "message": "msg...",
        "result": "q_not_found"
    }
    ```
    - *invalid email format* -> `http code: 400`
    ```json 
    {
        "data": {
            "invalid": {
                "email": "msg..."
            },
        },
        "message": "msg...",
        "result": "error"
    }
    ```