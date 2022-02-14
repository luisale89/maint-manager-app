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

* *body*
    ```javascript
    null
    ```

* *responses*
    - success:
        