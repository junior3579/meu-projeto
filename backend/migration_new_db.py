
import pg8000
import os
from backend.database_config import DB_CONFIG

def migrar_banco():
    # Aqui o usuário deve fornecer as novas credenciais
    # Por enquanto, vamos simular a alteração na estrutura do banco atual
    # para incluir o conceito de 'posicao'
    
    queries = [
        # Adicionar coluna posicao na tabela usuarios se não existir
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS posicao INT;",
        
        # Criar um índice para busca rápida por posição
        "CREATE INDEX IF NOT EXISTS idx_usuarios_posicao ON usuarios(posicao);",
        
        # Lógica para preencher posições iniciais para usuários existentes
        """
        DO $$
        DECLARE
            r RECORD;
            pos INT := 1;
        BEGIN
            FOR r IN SELECT id FROM usuarios ORDER BY id LOOP
                UPDATE usuarios SET posicao = pos WHERE id = r.id;
                pos := pos + 1;
            END LOOP;
        END $$;
        """
    ]
    
    conn = pg8000.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        for q in queries:
            cursor.execute(q)
        conn.commit()
        print("Migração concluída com sucesso!")
    except Exception as e:
        print(f"Erro na migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrar_banco()
