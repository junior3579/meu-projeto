
import pg8000
import os
import sys

# Adicionar o diretório pai ao sys.path para importar database_config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database_config import DB_CONFIG

def setup_database():
    conn = pg8000.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    queries = [
        # 1. Tabela usuarios
        '''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            reais INTEGER NOT NULL DEFAULT 0,
            whatsapp TEXT,
            pix_tipo TEXT,
            pix_chave TEXT,
            last_seen TEXT,
            posicao INTEGER
        )
        ''',
        # 2. Tabela categorias
        '''
        CREATE TABLE IF NOT EXISTS categorias (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE
        )
        ''',
        # 3. Tabela salas
        '''
        CREATE TABLE IF NOT EXISTS salas (
            id_sala SERIAL PRIMARY KEY,
            nome_sala TEXT NOT NULL,
            valor_inicial INTEGER NOT NULL,
            criador TEXT NOT NULL,
            jogadores TEXT,
            whatsapp TEXT,
            categoria_id INTEGER REFERENCES categorias(id),
            status TEXT DEFAULT 'aberta',
            vencedor_id INTEGER
        )
        ''',
        # 4. Tabela apostas
        '''
        CREATE TABLE IF NOT EXISTS apostas (
            id SERIAL PRIMARY KEY,
            id_sala INTEGER NOT NULL REFERENCES salas(id_sala),
            id_usuario INTEGER NOT NULL REFERENCES usuarios(id),
            valor_aposta INTEGER NOT NULL,
            status TEXT DEFAULT 'pendente',
            resultado TEXT DEFAULT 'pendente'
        )
        ''',
        # 5. Tabela transacoes
        '''
        CREATE TABLE IF NOT EXISTS transacoes (
            id SERIAL PRIMARY KEY,
            id_usuario INTEGER NOT NULL REFERENCES usuarios(id),
            tipo TEXT NOT NULL,
            valor INTEGER NOT NULL,
            status TEXT DEFAULT 'pendente',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''',
        # 6. Tabela torneios
        '''
        CREATE TABLE IF NOT EXISTS torneios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            status TEXT DEFAULT 'inscricao',
            vencedor_id INTEGER REFERENCES usuarios(id),
            valor_inscricao INTEGER DEFAULT 0,
            premio INTEGER DEFAULT 0,
            data_inicio TEXT,
            data_fim TEXT,
            fase_atual TEXT DEFAULT 'inscricao'
        )
        ''',
        # 7. Tabela torneio_participantes
        '''
        CREATE TABLE IF NOT EXISTS torneio_participantes (
            id SERIAL PRIMARY KEY,
            torneio_id INTEGER NOT NULL REFERENCES torneios(id),
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            status TEXT DEFAULT 'ativo',
            chave_id INTEGER,
            adversario_id INTEGER
        )
        ''',
        # 8. Tabela torneio_confrontos
        '''
        CREATE TABLE IF NOT EXISTS torneio_confrontos (
            id SERIAL PRIMARY KEY,
            torneio_id INTEGER NOT NULL REFERENCES torneios(id),
            fase_nome TEXT NOT NULL,
            jogador1_id INTEGER REFERENCES usuarios(id),
            jogador2_id INTEGER REFERENCES usuarios(id),
            vencedor_id INTEGER REFERENCES usuarios(id),
            status TEXT DEFAULT 'pendente'
        )
        ''',
        # 9. Tabela torneio_fases
        '''
        CREATE TABLE IF NOT EXISTS torneio_fases (
            id SERIAL PRIMARY KEY,
            torneio_id INTEGER NOT NULL REFERENCES torneios(id),
            nome_fase TEXT NOT NULL,
            ordem INTEGER NOT NULL,
            status TEXT DEFAULT 'pendente',
            participantes_ids TEXT,
            vencedores_ids TEXT
        )
        ''',
        # Adicionar colunas extras caso as tabelas já existam
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS reais INTEGER DEFAULT 0;",
        "ALTER TABLE salas ADD COLUMN IF NOT EXISTS vencedor_id INTEGER;",
        "ALTER TABLE salas ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'aberta';",
        "ALTER TABLE torneios ADD COLUMN IF NOT EXISTS valor_inscricao INTEGER DEFAULT 0;",
        "ALTER TABLE torneios ADD COLUMN IF NOT EXISTS premio INTEGER DEFAULT 0;",
        "ALTER TABLE torneios ADD COLUMN IF NOT EXISTS fase_atual TEXT DEFAULT 'inscricao';",
        "ALTER TABLE torneios ADD COLUMN IF NOT EXISTS data_inicio TEXT;",
        "ALTER TABLE torneios ADD COLUMN IF NOT EXISTS data_fim TEXT;",
        "ALTER TABLE torneio_participantes ADD COLUMN IF NOT EXISTS chave_id INTEGER;",
        "ALTER TABLE torneio_participantes ADD COLUMN IF NOT EXISTS adversario_id INTEGER;"
    ]
    
    try:
        for query in queries:
            print(f"Executando: {query[:50]}...")
            cursor.execute(query)
        conn.commit()
        print("Banco de dados configurado com sucesso!")
    except Exception as e:
        print(f"Erro ao configurar banco de dados: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    setup_database()
