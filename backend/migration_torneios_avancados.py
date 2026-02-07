"""
Script de migração para adicionar funcionalidades avançadas de torneios
- Adicionar campo valor_inscricao e premio na tabela torneios
- Criar tabela torneio_fases para sistema de classificatória
- Adicionar campo vencedor_id na tabela salas
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "stake_arena_local.db")

def executar_migracao():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Adicionar novos campos na tabela torneios
        print("Adicionando campos valor_inscricao e premio na tabela torneios...")
        try:
            cursor.execute("ALTER TABLE torneios ADD COLUMN valor_inscricao INTEGER DEFAULT 0")
            print("✓ Campo valor_inscricao adicionado")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ Campo valor_inscricao já existe")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE torneios ADD COLUMN premio INTEGER DEFAULT 0")
            print("✓ Campo premio adicionado")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ Campo premio já existe")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE torneios ADD COLUMN fase_atual TEXT DEFAULT 'inscricao'")
            print("✓ Campo fase_atual adicionado")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ Campo fase_atual já existe")
            else:
                raise
        
        # 2. Criar tabela de fases do torneio
        print("\nCriando tabela torneio_fases...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS torneio_fases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                torneio_id INTEGER NOT NULL,
                nome_fase TEXT NOT NULL,
                ordem INTEGER NOT NULL,
                status TEXT DEFAULT 'pendente',
                participantes_ids TEXT,
                vencedores_ids TEXT,
                FOREIGN KEY(torneio_id) REFERENCES torneios(id)
            )
        """)
        print("✓ Tabela torneio_fases criada")
        
        # 3. Adicionar campo vencedor_id na tabela salas
        print("\nAdicionando campo vencedor_id na tabela salas...")
        try:
            cursor.execute("ALTER TABLE salas ADD COLUMN vencedor_id INTEGER")
            print("✓ Campo vencedor_id adicionado")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ Campo vencedor_id já existe")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE salas ADD COLUMN status TEXT DEFAULT 'ativa'")
            print("✓ Campo status adicionado")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ Campo status já existe")
            else:
                raise
        
        conn.commit()
        print("\n✅ Migração concluída com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erro durante a migração: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    executar_migracao()
