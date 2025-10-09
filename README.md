# Silo Monitor Backend

Sistema backend moderno para monitoramento inteligente de silos de soja, utilizando FastAPI, MongoDB, notificações push e automação de tarefas agendadas.

 <!-- Substitua pelo seu próprio GIF de demo assim que possível -->

***

## 🚀 Tecnologias Utilizadas

| Tecnologia        | Função                                    |
|-------------------|--------------------------------------------|
| FastAPI           | API REST principal [1]  |
| Uvicorn           | Servidor ASGI rápido [1] |
| MongoDB + Motor   | Persistência NoSQL, driver async [1] |
| Pydantic          | Validação e serialização de dados [1] |
| APScheduler       | Tarefas agendadas (coleta, atualização) [1] |
| JWT/PyJWT         | Autenticação segura via token [1] |
| python-dotenv     | Gerenciamento de variáveis ambiente [1] |
| Docker Compose    | Integração e deploy local/dev[2]    |
| Pytest            | Testes automatizados[1]             |

***

## 📦 Estrutura do Projeto

- **app/**: Módulos FastAPI, rotas e serviços principais
- **app/main.py**: Entrypoint da API
- **app/config.py**: Configurações globais
- **app/db.py**: Integração com banco MongoDB
- **app/routes/**: Endpoints organizados
- **app/services/**: Lógica do domínio/silo/Notificações
- **app/tasks/**: Jobs agendados (ex: ingestão periódica)
- **app/models/** e **app/schemas.py**: Esquemas de dados (ORM/Pydantic)
- **requirements.txt**: Dependências Python
- **.env.example**: Template das variáveis ambiente
- **Dockerfile**, **docker-compose.yml**: Facilita deploy/dev local
- **scripts/**: Utilitários de inicialização/admin
- **tests/**: Testes automatizados com Pytest[2]

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

3. **Configuração de variáveis**
   ```sh
   cp .env.example .env
   `
   # Edite .env com seus dados (MONGODB_URI, JWT_SECRET, VAPID_PUBLIC_KEY etc.)
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

| Método | Rota                  | Descrição                       |
|--------|-----------------------|---------------------------------|
| GET    | /api/health           | Status do backend/MongoDB[2] |
| GET    | /docs                 | Documentação interativa[2] |
| POST   | /api/silo             | Registrar novo silo             |
| GET    | /api/silo/{id}        | Consultar dados de silo         |
| POST   | /api/notify           | Notificações push/web           |

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

- Nunca submeta `.env` ao git!
- Use variáveis secretas para produção (Render, AWS Secrets)
- Permissões mínimas para usuários MongoDB[2]