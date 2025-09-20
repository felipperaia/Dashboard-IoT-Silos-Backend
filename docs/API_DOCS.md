# API_DOCS (resumo)

POST /api/auth/login
- body: { "username", "password" }
- retorna: { access_token, refresh_token }

POST /api/auth/seed-admin
- body: {username,email,password}, secret no body
- cria primeiro admin apenas se nenhum existir

GET /api/users (admin)
POST /api/users (admin)
PUT /api/users/{id} (admin)
DELETE /api/users/{id} (admin)

GET /api/silos
POST /api/silos (admin)
PUT /api/silos/{id}/settings

POST /api/readings
- body: ReadingIn
- usada pelo job ThingSpeak

GET /api/alerts
POST /api/alerts/ack/{id}

POST /api/ml/retrain
GET /api/ml/status

...examples omitted for brevidade...
