# API v1 endpoints

Documentacion sobre los endpoints de la app.

#

## auth endpoints

```base_url = {{URL}}/api/v1/auth```

### 1. email-query endpoint - open endpoint
---
endpoint para consultar la existencia de un email en la app

**headers**

```json
{
    "content-type": "application/json"
}
```

**endpoint**

```http
GET {{base_url}}/email-query?email={{valid_email}}
```

**response**

