# Guia de Implantação do Projeto Let's Play no Render

Este guia detalha os passos necessários para implantar o projeto Let's Play no Render, utilizando um único serviço web para o backend Python (Flask com Socket.IO) e servindo os arquivos estáticos do frontend (React/Vite).

## 1. Configuração do Banco de Dados (Neon.tech ou Supabase)

O projeto está configurado para usar um banco de dados PostgreSQL. Recomenda-se o uso de serviços como [Neon.tech](https://neon.tech) ou Supabase para hospedar seu banco de dados. Se você já possui um banco de dados, siga estes passos:

1.  **Obtenha as Credenciais:** Acesse o painel do seu provedor de banco de dados (Neon.tech ou Supabase) e localize as credenciais de conexão: **usuário**, **senha**, **host**, **nome do banco de dados** e **porta**. Certifique-se de que o SSL esteja ativado.
2.  **Variáveis de Ambiente:** Estas credenciais serão configuradas como variáveis de ambiente no Render. O arquivo `backend/database_config.py` foi atualizado para ler essas variáveis. As chaves esperadas são:
    *   `DB_USER`
    *   `DB_PASSWORD`
    *   `DB_HOST`
    *   `DB_NAME`
    *   `DB_PORT`
    *   `DB_SSL` (defina como `True`)

## 2. Preparação do Frontend para Deploy

O backend Python está configurado para servir os arquivos estáticos do frontend. Portanto, é necessário construir o frontend e colocar os arquivos gerados na pasta `backend/static`.

1.  **Instale as Dependências do Frontend:** Navegue até a raiz do projeto (`/home/ubuntu/lets-play`) e instale as dependências do frontend usando `pnpm`:
    ```bash
    pnpm install
    ```
2.  **Construa o Frontend:** Após a instalação, construa o projeto frontend. O `vite.config.js` deve ser configurado para gerar a saída na pasta `backend/static`.
    ```bash
    pnpm run build
    ```
    *Certifique-se de que o comando `build` no `package.json` esteja configurado para gerar os arquivos na pasta correta. Se não estiver, você precisará ajustar o `vite.config.js` ou o comando de build para que a saída seja direcionada para `backend/static`.*

## 3. Deploy do Backend no Render

O Render pode ser configurado usando um arquivo `render.yaml` (Blueprint) para automatizar a criação do serviço. O arquivo `render.yaml` já foi criado na raiz do seu projeto.

1.  **Crie um Repositório Git:** Se ainda não o fez, inicialize um repositório Git na raiz do seu projeto e faça o commit de todos os arquivos, incluindo o `render.yaml` e os arquivos de build do frontend (`backend/static`). Em seguida, envie-o para um serviço como GitHub, GitLab ou Bitbucket.
2.  **Conecte ao Render:**
    *   Acesse [Render.com](https://render.com) e faça login.
    *   No seu painel, clique em "New" e selecione "Blueprint".
    *   Conecte seu repositório Git onde o projeto está hospedado.
    *   O Render detectará automaticamente o arquivo `render.yaml`.
3.  **Configuração do Serviço (via `render.yaml`):** O arquivo `render.yaml` já pré-configura o serviço web com as seguintes definições:
    *   **Tipo:** Web Service
    *   **Nome:** `lets-play-backend`
    *   **Runtime:** Python
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT backend.main:app`
    *   **Variáveis de Ambiente:** As variáveis `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME`, `DB_PORT`, `DB_SSL` e `SECRET_KEY` estão listadas. Você precisará preencher os valores para as credenciais do seu banco de dados e uma `SECRET_KEY` forte. O Render pode gerar automaticamente uma `SECRET_KEY` para você.
4.  **Deploy:** Confirme as configurações e inicie o deploy. O Render construirá e implantará seu serviço.

## 4. Variáveis de Ambiente Essenciais

Certifique-se de definir as seguintes variáveis de ambiente no painel do Render para o seu serviço web:

| Variável       | Descrição                                                              | Exemplo                                   |
| :------------- | :--------------------------------------------------------------------- | :---------------------------------------- |
| `DB_USER`      | Usuário do banco de dados PostgreSQL.                                  | `postgres.kubvbqvpuwecrlwwmrvc`           |
| `DB_PASSWORD`  | Senha do usuário do banco de dados.                                    | `SuaSenhaSegura123`                       |
| `DB_HOST`      | Host do servidor do banco de dados.                                    | `aws-1-sa-east-1.pooler.supabase.com`     |
| `DB_NAME`      | Nome do banco de dados (geralmente `postgres`).                        | `postgres`                                |
| `DB_PORT`      | Porta do banco de dados (geralmente `5432`).                           | `5432`                                    |
| `DB_SSL`       | Define se a conexão SSL é usada.                                       | `True`                                    |
| `SECRET_KEY`   | Chave secreta para segurança da aplicação Flask. **Gerar uma nova!** | `uma_chave_secreta_muito_longa_e_segura` |


## 5. Considerações Finais

*   **Atualizações:** Sempre que houver alterações no código, faça o commit e push para o seu repositório Git. O Render pode ser configurado para fazer o deploy automático a cada push.
*   **Logs:** Monitore os logs do seu serviço no painel do Render para depurar quaisquer problemas que possam surgir durante o deploy ou a execução.
*   **Domínio Personalizado:** Após o deploy, você pode configurar um domínio personalizado para seu serviço no Render.

Com estes passos, seu projeto Let's Play estará online no Render!
