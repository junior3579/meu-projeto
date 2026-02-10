import pg8000
import os
import sys
from decimal import Decimal

# Adicionar o diretório pai ao sys.path para importar database_config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database_config import DB_CONFIG

def migrate():
    print("Iniciando migração para DECIMAL e melhorias de desempenho...")
    conn = pg8000.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    queries = [
        # Converter colunas para DECIMAL(15,2)
        "ALTER TABLE usuarios ALTER COLUMN reais TYPE DECIMAL(15,2) USING reais::DECIMAL(15,2)",
        "ALTER TABLE salas ALTER COLUMN valor_inicial TYPE DECIMAL(15,2) USING valor_inicial::DECIMAL(15,2)",
        "ALTER TABLE apostas ALTER COLUMN valor_aposta TYPE DECIMAL(15,2) USING valor_aposta::DECIMAL(15,2)",
        "ALTER TABLE transacoes ALTER COLUMN valor TYPE DECIMAL(15,2) USING valor::DECIMAL(15,2)",
        "ALTER TABLE torneios ALTER COLUMN valor_inscricao TYPE DECIMAL(15,2) USING valor_inscricao::DECIMAL(15,2)",
        "ALTER TABLE torneios ALTER COLUMN premio TYPE DECIMAL(15,2) USING premio::DECIMAL(15,2)",
        
        # Adicionar índices para melhor desempenho
        "CREATE INDEX IF NOT EXISTS idx_usuarios_nome ON usuarios(nome)",
        "CREATE INDEX IF NOT EXISTS idx_usuarios_posicao ON usuarios(posicao)",
        "CREATE INDEX IF NOT EXISTS idx_salas_status ON salas(status)",
        "CREATE INDEX IF NOT EXISTS idx_salas_criador ON salas(criador)",
        "CREATE INDEX IF NOT EXISTS idx_apostas_sala ON apostas(id_sala)",
        "CREATE INDEX IF NOT EXISTS idx_apostas_usuario ON apostas(id_usuario)",
        "CREATE INDEX IF NOT EXISTS idx_transacoes_usuario ON transacoes(id_usuario)",
        "CREATE INDEX IF NOT EXISTS idx_torneio_participantes_torneio ON torneio_participantes(torneio_id)",
        "CREATE INDEX IF NOT EXISTS idx_torneio_confrontos_torneio ON torneio_confrontos(torneio_id)"
    ]
    
    try:
        for query in queries:
            print(f"Executando: {query}")
            cursor.execute(query)
        conn.commit()
        print("\n✅ Migração concluída com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro na migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
