# Deploy

Backend (Render)
- Criar novo Web Service em Render: apontar para backend, comando de start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
- Configurar variáveis de ambiente no dashboard do Render (MONGO_URI, JWT_SECRET, etc).

Frontend (Netlify)
- Build: npm run build (Vite).
- Configurar site no Netlify e adicionar env vars VAPID_PUBLIC_KEY, API_URL.

MongoDB Atlas
- Criar cluster, criar usuário com senha, adicionar network access (IPs) e setar MONGO_URI.
