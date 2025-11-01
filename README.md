# Silo Monitor Backend

Sistema backend moderno para monitoramento inteligente de silos de grãos via ThingSpeak, utilizando FastAPI, MongoDB, múltiplos canais de notificação (email, SMS, Telegram, WebSocket), chatbot LLM e autenticação MFA.

## ✨ Funcionalidades

- ♨️ Monitoramento em tempo real de temperatura, umidade e gases
- 🤖 Chatbot LLM via OpenRouter/DeepSeek para suporte
- 📱 MFA com TOTP (compatível com Microsoft Authenticator)
- 📨 Notificações multicanal:
  - Email via SendGrid
  - SMS via Twilio
  - Mensagens Telegram
  - Web Push Notifications
  - WebSocket para alertas em tempo real
- 📊 Relatórios avançados com métricas estatísticas
- ⚡ API REST + WebSocket para integração front-end
- 🔄 Integração automática com ThingSpeak

***

## 🚀 Tecnologias Utilizadas

| Tecnologia        | Função                                    |
|-------------------|--------------------------------------------|
| FastAPI 0.95.2+   | Framework web assíncrono  |
| MongoDB + Motor   | Banco de dados NoSQL assíncrono |
| ThingSpeak API    | Integração IoT para leitura de sensores |
| SendGrid          | Envio de emails |
| Twilio            | Envio de SMS |
| Telegram Bot API  | Mensagens via Telegram |
| WebPush          | Notificações web push |
| WebSocket        | Alertas em tempo real |
| OpenRouter API    | Chatbot LLM/IA |
| PyOTP            | MFA com TOTP |
| JWT + OAuth2     | Autenticação e autorização |
| APScheduler      | Agendamento de tarefas |
| Pydantic         | Validação e serialização |

***

## 📦 Estrutura do Projeto

```
.
├── app/                    # Módulo principal
│   ├── main.py            # Entrypoint da API
│   ├── config.py          # Configurações globais
│   ├── db.py              # Conexão MongoDB
│   ├── auth.py            # Autenticação (JWT+MFA)
│   ├── schemas.py         # Modelos Pydantic
│   ├── utils.py           # Utilitários
│   ├── routes/            # Endpoints da API
│   │   ├── alerts.py      # Gestão de alertas
│   │   ├── auth.py        # Login/MFA
│   │   ├── silos.py       # CRUD de silos
│   │   ├── readings.py    # Leituras sensores
│   │   └── ...           
│   ├── services/          # Lógica de negócio
│   │   ├── notification.py    # Multi-canal
│   │   └── thing_speak.py     # Integração IoT
│   └── tasks/             # Jobs agendados
│       └── scheduler.py    # Coleta periódica
├── requirements.txt       # Dependências Python
├── runtime.txt           # Versão Python
├── Makefile             # Comandos úteis
└── .env.example         # Template config
```

***

## ⚡️ Como Rodar Localmente

1. **Clone o repositório**
   ```sh
   git clone <nosso repositorio>
   cd <repositorio>
   ```

2. **Configure o ambiente Python**
   ```sh
   python -m venv .venv
   source .venv/bin/activate        # (Linux/Mac)
   .\.venv\Scripts\Activate.ps1     # (Windows)
   ```

3. **Configuração de variáveis (.env)**
   ```ini
   # Banco
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB=silo_db

   # JWT Auth
   JWT_SECRET=seu_secret_aqui
   JWT_ACCESS_EXPIRE_MIN=15
   JWT_REFRESH_EXPIRE_DAYS=7

   # SendGrid SMTP
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USER=apikey
   SMTP_PASS=sua_sendgrid_api_key
   SMTP_FROM=no-reply@seu-dominio.com

   # Twilio SMS
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_FROM=+1234567890

   # Telegram Bot
   TELEGRAM_BOT_TOKEN=123:ABC...
   TELEGRAM_DEFAULT_CHAT_ID=123456

   # Web Push
   VAPID_PUBLIC_KEY=...
   VAPID_PRIVATE_KEY=...

   # OpenRouter/LLM
   OPENROUTER_API_KEY=sk-...
   OPENROUTER_MODEL=deepseek/deepseek-r1-distill-qwen-32b
   LLM_SYSTEM_PROMPT="Você é um assistente especializado..."

   # ThingSpeak
   THINGSPEAK_API_KEYS={"1":"ABC123"}
   THINGSPEAK_CHANNELS={"1":"3082805"}
   ```

4. **Instale as dependências**
   ```sh
   python -m pip install --upgrade pip wheel setuptools
   pip install -r requirements.txt
   ```

5. **Inicialize banco/admin**
   ```sh
   python scripts/seed_admin.py --username admin --email minh@empresa.com --password Minhasenha123 --secret <INIT_ADMIN_SECRET>
   ```

6. **Inicie em desenvolvimento**
   ```sh
   python -m uvicorn app.main:app --reload --port 8000
   ```

7. **Acesse:**
   - Endpoint saúde: [http://localhost:8000/api/health](http://localhost:8000/api/health)
   - Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

***

## 🔥 Principais Endpoints

### Silos e Leituras

- `GET /api/silos` - Lista silos
- `POST /api/silos` - Cria silo  
- `GET /api/silos/{id}` - Detalhes do silo
- `PUT /api/silos/{id}` - Atualiza silo
- `POST /api/silos/import_thingspeak` - Importa do ThingSpeak
- `GET /api/silos/{id}/readings` - Leituras do silo
- `POST /api/silos/{id}/refresh` - Atualiza dados ThingSpeak

### Notificações e Alertas

- `ws://host/api/alerts/ws` - WebSocket para alertas real-time
- `GET /api/alerts/feed` - Feed de alertas (polling)
- `POST /api/notify/test` - Testa notificações

### Chatbot e MFA

- `POST /api/chat` - Conversa com LLM (contexto do DB)
- `POST /api/mfa/setup` - Setup inicial MFA/TOTP
- `POST /api/mfa/verify` - Valida token MFA

### Relatórios

- `POST /api/reports` - Gera relatório
- `GET /api/reports` - Lista relatórios
- `GET /api/reports/{id}` - Detalhes do relatório

***

## 🛠 Comandos Úteis

- Gerar chaves VAPID para push:
  ```sh
  npx web-push generate-vapid-keys --json
  ```

- Testes automatizados:
  ```sh
  pytest
  ```

- Run na Docker Compose (MongoDB + Backend):
  ```sh
  docker-compose up
  ```

***

## 🌱 Dicas para Contribuição

- Forke o projeto
- Use branches temáticos para novas features/fixes
- Mantenha testes automáticos atualizados
- Dúvidas/críticas: abra uma issue

***

## 🚨 Segurança

- 🔒 Nunca submeta `.env` ao git!
- 🔑 Use variáveis secretas em produção
- 🛡️ MFA habilitado por padrão para contas sensíveis
- 📝 Todas as ações são logadas para auditoria
- 🔐 JWT com refresh tokens e expiração curta
- 🌐 CORS configurado apenas para origens confiáveis
- 🔒 Rate limiting em endpoints sensíveis
- 💾 Backup automático do MongoDB

## 📚 Documentação

- 📖 API Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📝 ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- 💡 Postman Collection: [Link](./postman_collection.json)

## 🤝 Suporte

- 📧 Email: suporte@empresa.com
- 💬 Issues no GitHub
- 🤖 Chatbot no próprio sistema

## Notas rápidas sobre MFA e notificações

- O backend expõe endpoints para MFA (TOTP) em `/api/mfa/setup` e `/api/mfa/verify`.
- Notificações suportadas: WebPush (pywebpush), Telegram (bot), Email (SMTP) e SMS (Twilio). Configure as variáveis correspondentes no `.env`.
- Para WebPush gere chaves VAPID com `npx web-push generate-vapid-keys --json` e cole no `.env`.