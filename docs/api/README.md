# API

Canonical API contract is FastAPI OpenAPI.

Prefix:

```text
/api/v1
```

Health endpoints are outside version prefix:

```text
/health/live
/health/ready
```

Generate schema:

```bash
make openapi
```
