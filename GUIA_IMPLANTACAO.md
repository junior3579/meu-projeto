# Guia de Implantação Permanente - Let's Play

Este guia explica como hospedar seu site de forma definitiva e profissional.

## 1. Banco de Dados (Neon.tech)
Você já está usando o Neon, o que é ótimo! Para a implantação permanente:
1. Acesse seu painel no [Neon.tech](https://neon.tech).
2. Copie a **Connection String** (URL de conexão).
3. Você usará esses dados nas variáveis de ambiente do servidor.

## 2. Hospedagem do Backend (Render.com ou Railway.app)
Recomendo o **Render** por ser fácil e ter plano gratuito:
1. Crie uma conta no [Render.com](https://render.com).
2. Conecte seu repositório do GitHub (onde você deve subir os arquivos deste projeto).
3. Escolha **Web Service**.
4. Configure:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT backend.main:app`
5. Em **Environment Variables**, adicione as variáveis do arquivo `.env.example`.

## 3. Hospedagem do Frontend (Vercel ou Netlify)
Para o frontend ser rápido e gratuito:
1. Crie uma conta na [Vercel](https://vercel.com).
2. Importe seu repositório.
3. A Vercel detectará automaticamente o projeto React/Vite.
4. Configure a variável de ambiente `VITE_API_URL` apontando para a URL do seu backend no Render.

## 4. Arquivos Importantes
- `Dockerfile`: Caso prefira usar Docker.
- `requirements.txt`: Lista de todas as dependências necessárias.
- `.env.example`: Modelo de como configurar suas senhas e acessos.

---
**Dica:** Mantenha suas chaves de banco de dados sempre em segredo e nunca as envie diretamente para o GitHub público!
