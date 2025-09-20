# Backend — Silo Monitor (FastAPI)

Este diretório é o núcleo do serviço backend e deve ser o conteúdo do repositório "silo-monitor-backend".

Arquivos/dirs que pertencem ao repositório backend
- app/ (código FastAPI):
  - app/main.py
  - app/config.py
  - app/db.py
  - app/routes/
  - app/services/
  - app/ml/
  - app/tasks/
  - app/models/ e app/schemas.py
- requirements.txt
- scripts/
  - seed_admin.py
  - generate_vapid.py
- .env.example (template)
- Dockerfile (opcional)
- docker-compose.yml (opcional para dev)
- tests/ (pytest)
- Makefile (opcional)
- README.md (este arquivo)
- .gitignore (ver abaixo)

Quickstart local (Windows)
1. Clone o repositório backend:
   git clone <url-do-repo-backend>
   cd silo-monitor-backend

2. Crie e ative virtualenv:
   python -m venv .venv .\.venv\Scripts\Activate.ps1

3. Copie o template de variáveis:
   copy .env.example .env
   # edite backend/.env com suas credenciais (MONGO_URI, JWT_SECRET, INIT_ADMIN_SECRET, VAPID keys, etc)

4. Atualize instaladores e instale dependências:
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt

5. Inicie em desenvolvimento:
   python -m uvicorn app.main:app --reload --port 8000

Gerar VAPID keys (recomendado)
- No projeto frontend (ou na raiz), execute:
  npx web-push generate-vapid-keys --json
  copie publicKey -> VAPID_PUBLIC_KEY e privateKey -> VAPID_PRIVATE_KEY em backend/.env

Seed do admin
- scripts/seed_admin.py usa INIT_ADMIN_SECRET para criar o primeiro admin:
  INIT_ADMIN_SECRET=<secret> python scripts/seed_admin.py --username admin --email a@b.com --password "Pass123" --secret <secret>

Docker / docker-compose (dev)
- O repositório inclui docker-compose.yml para facilitar dev local com Mongo.
- Ajuste MONGO_URI no backend/.env se usando compose (mongodb://mongo:27017/silo).

Health / Debug
- GET /api/health — verifica ping no MongoDB.
- Logs: execute `python -m uvicorn app.main:app --reload` para ver tracebacks completos.

.gitignore sugerido (crie no repo)
# Python
.env
.venv/
__pycache__/
*.pyc
*.pyo
.Python

# Editor
.vscode/
.idea/

# Logs
*.log

Segurança
- Nunca comite backend/.env
- Use secret manager do provedor (Render secrets) para variáveis de produção
- Permissões mínimas para o usuário MongoDB Atlas

Migrando do monorepo
- Copie os arquivos listados na seção "Arquivos/dirs que pertencem ao repositório backend" para o novo repo e preserve histórico com git-filter-repo se desejar.

Recriar ambiente e instalar dependências (após atualização de requirements)
-------------------------------------------------------------------------------------------------------------------------------------------
1. Remova o virtualenv atual (se quiser começar limpo):
   Remove-Item -Recurse -Force .venv

2. Crie e ative um novo venv (use Python 3.11 recomendado):
   "C:\caminho\para\Python311\python.exe" -m venv .venv
   .\.venv\Scripts\Activate.ps1

3. Atualize instaladores e instale requirements:
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt

   Observação: fizemos pin do pymongo para evitar incompatibilidade com motor.
   Se tiver problemas, remova .venv e repita os passos acima.

4. Inicie o servidor:
   python -m uvicorn app.main:app --reload --port 8000

Verificação rápida
- Health: http://localhost:8000/api/health
- Docs:   http://localhost:8000/docs

Se após reinstalar voltar outro erro, cole as últimas ~50 linhas do log aqui e eu analiso.

Recomendação sobre virtualenv
- É recomendado criar o venv DENTRO da pasta backend para evitar ambiguidade:
  cd backend
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1

- Caso o .venv esteja na raiz do projeto, o script run_dev.ps1 agora detecta e tenta ativá-lo,
  mas o local preferencial é backend/.venv.

- Se mudou de Python (ex.: para 3.11), recrie o venv:
  Remove-Item -Recurse -Force .venv
  "C:\Path\To\Python311\python.exe" -m venv .venv
  .\.venv\Scripts\Activate.ps1
  python -m pip install --upgrade pip setuptools wheel
  pip install -r requirements.txt
