# CORS Policy (Backend Aggregator)

Backend Aggregator CORS is controlled via config (`cors` in `config/default.yaml`).

## Default Policy
- Allowed origins:
  - `https://www.figma.com`
  - `https://figma.com`
  - Regex: `^https://([a-z0-9-]+\.)*figma\.com$`
- Allowed methods: `GET`, `POST`, `OPTIONS`
- Allowed headers: `Content-Type`, `X-API-Key`, `X-Role`
- Credentials: `false`
- Max age: `86400`

## Override
Create an override config file and set `NDEFENDER_CONFIG`.

Example override:
```yaml
cors:
  allow_origins:
    - "https://www.figma.com"
    - "https://figma.com"
    - "https://staging.figma.com"
  allow_origin_regex: "^https://([a-z0-9-]+\\.)*figma\\.com$"
  allow_methods: ["GET", "POST", "OPTIONS"]
  allow_headers: ["Content-Type", "X-API-Key", "X-Role"]
  allow_credentials: false
  max_age: 86400
```

Apply:
```bash
export NDEFENDER_CONFIG=/opt/ndefender/config/override.yaml
```

## Preflight Test (OPTIONS)
```bash
curl -i -X OPTIONS https://n.flyspark.in/api/v1/status \
  -H "Origin: https://www.figma.com" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: X-API-Key, X-Role, Content-Type"
```

Expected headers:
- `Access-Control-Allow-Origin: https://www.figma.com`
- `Access-Control-Allow-Methods: GET,POST,OPTIONS`
- `Access-Control-Allow-Headers: Content-Type,X-API-Key,X-Role`
- `Access-Control-Allow-Credentials: false`
