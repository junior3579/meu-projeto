
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
        # Criar tabela de configurações se não existir
        '''
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
        ''',
        # Inserir senha padrão do admin se não existir
        "INSERT INTO configuracoes (chave, valor) VALUES ('admin_password', '3579') ON CONFLICT (chave) DO NOTHING",
        # Inserir whatsapp padrão do admin se não existir
        "INSERT INTO configuracoes (chave, valor) VALUES ('admin_whatsapp', '5511999999999') ON CONFLICT (chave) DO NOTHING",
        # Garantir que a tabela cofre_total existe
        '''
        CREATE TABLE IF NOT EXISTS cofre_total (
            id INTEGER PRIMARY KEY,
            valor_total NUMERIC DEFAULT 0,
            ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''',
        "INSERT INTO cofre_total (id, valor_total) VALUES (1, 0) ON CONFLICT (id) DO NOTHING",
        # Garantir que a tabela cofre_historico existe
        '''
        CREATE TABLE IF NOT EXISTS cofre_historico (
            id SERIAL PRIMARY KEY,
            id_sala INTEGER,
            valor NUMERIC,
            data_recebimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            descricao TEXT,
            tipo_transacao TEXT
        )
        '''
    ]
    
    try:
        for query in queries:
            cursor.execute(query)
        conn.commit()
        print("Migração de configurações administrativas concluída com sucesso!")
    except Exception as e:
        print(f"Erro na migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
