
import pg8000
import os
import sys

# Adicionar o diretório pai ao sys.path para importar database_config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database_config import DB_CONFIG

def migrate():
    conn = pg8000.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    queries = [
        # 1. Garantir que a tabela torneios tem todos os campos
        "ALTER TABLE torneios ADD COLUMN IF NOT EXISTS valor_inscricao INTEGER DEFAULT 0;",
        "ALTER TABLE torneios ADD COLUMN IF NOT EXISTS premio INTEGER DEFAULT 0;",
        "ALTER TABLE torneios ADD COLUMN IF NOT EXISTS fase_atual TEXT DEFAULT 'inscricao';",
        "ALTER TABLE torneios ADD COLUMN IF NOT EXISTS data_inicio TEXT;",
        "ALTER TABLE torneios ADD COLUMN IF NOT EXISTS data_fim TEXT;",
        
        # 2. Criar tabela torneio_participantes
        '''
        CREATE TABLE IF NOT EXISTS torneio_participantes (
            id SERIAL PRIMARY KEY,
            torneio_id INTEGER REFERENCES torneios(id) ON DELETE CASCADE,
            usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            status TEXT DEFAULT 'ativo', -- ativo, eliminado
            chave_id INTEGER,
            adversario_id INTEGER,
            data_inscricao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''',
        
        # 3. Criar tabela torneio_confrontos
        '''
        CREATE TABLE IF NOT EXISTS torneio_confrontos (
            id SERIAL PRIMARY KEY,
            torneio_id INTEGER REFERENCES torneios(id) ON DELETE CASCADE,
            fase_nome TEXT NOT NULL,
            jogador1_id INTEGER REFERENCES usuarios(id),
            jogador2_id INTEGER REFERENCES usuarios(id),
            vencedor_id INTEGER REFERENCES usuarios(id),
            status TEXT DEFAULT 'pendente' -- pendente, finalizado
        );
        ''',
        
        # 4. Criar tabela torneio_fases
        '''
        CREATE TABLE IF NOT EXISTS torneio_fases (
            id SERIAL PRIMARY KEY,
            torneio_id INTEGER REFERENCES torneios(id) ON DELETE CASCADE,
            nome_fase TEXT NOT NULL,
            ordem INTEGER NOT NULL,
            status TEXT DEFAULT 'pendente',
            participantes_ids TEXT,
            vencedores_ids TEXT
        );
        '''
    ]
    
    try:
        for query in queries:
            print(f"Executando: {query[:50]}...")
            cursor.execute(query)
        conn.commit()
        print("\n✅ Migração do Supabase concluída com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro na migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
