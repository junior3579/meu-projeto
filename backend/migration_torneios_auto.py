import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "stake_arena_local.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Adicionar campos de data na tabela torneios
        print("Adicionando campos de data na tabela torneios...")
        cursor.execute("ALTER TABLE torneios ADD COLUMN data_inicio TEXT")
        cursor.execute("ALTER TABLE torneios ADD COLUMN data_fim TEXT")
        print("✓ OK")
        
        # Adicionar campo de chave/dupla na tabela torneio_participantes
        print("Adicionando campo de chave na tabela torneio_participantes...")
        cursor.execute("ALTER TABLE torneio_participantes ADD COLUMN chave_id INTEGER")
        cursor.execute("ALTER TABLE torneio_participantes ADD COLUMN adversario_id INTEGER")
        print("✓ OK")
        
        # Criar tabela para gerenciar as chaves/confrontos do torneio
        print("Criando tabela torneio_confrontos...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS torneio_confrontos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                torneio_id INTEGER NOT NULL,
                fase_nome TEXT NOT NULL,
                jogador1_id INTEGER,
                jogador2_id INTEGER,
                vencedor_id INTEGER,
                status TEXT DEFAULT 'pendente', -- pendente, em_andamento, finalizado
                FOREIGN KEY(torneio_id) REFERENCES torneios(id),
                FOREIGN KEY(jogador1_id) REFERENCES usuarios(id),
                FOREIGN KEY(jogador2_id) REFERENCES usuarios(id),
                FOREIGN KEY(vencedor_id) REFERENCES usuarios(id)
            )
        ''')
        print("✓ OK")
        
        conn.commit()
        print("Migração concluída com sucesso!")
    except Exception as e:
        print(f"Erro na migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
