# API v1 endpoints
---

`** auth endpoints **`
---


1. `GET` **email-query**

    endpoint para consultar la existencia de un email en la app

* *url*
    ```http
    GET /api/v1/auth/email-query?email="valid@email"
    ```

    | Parameter | Type | Description |
    | :--- | :--- | :--- |
    | `email` | `string` | **Required**. query email |

* *headers*
    ```json
    {
        "content-type":"application/json"
    }
    ```

* *response*
    - `http code: 200` - *success*
    ```json
    {
        "data": {},
        "message": "email {query-email} exists in database",
        "app_status": "success"
    }
    ```
    - `http code: 404` - *not found*
    ```json
    {
        "data": {},
        "message": "email {query-email} not found in database",
        "app_status": "error"
    }
    ```
    - `http code: 400` - *bad request*
    ```json 
    {
        "data": {},
        "message": "invalid {email-query}",
        "app_status": "error"
    }
    ```