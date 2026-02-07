
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "stake_arena_local.db")

def testar_reutilizacao():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Limpar tabela para o teste
    cursor.execute("DELETE FROM usuarios")
    conn.commit()
    
    print("1. Cadastrando usuários 1, 2 e 3...")
    for i in [1, 2, 3]:
        cursor.execute("INSERT INTO usuarios (id, nome, senha, reais, posicao) VALUES (?, ?, ?, ?, ?)", 
                       (i, f"User{i}", "123", 100, i))
    conn.commit()
    
    cursor.execute("SELECT id, nome FROM usuarios")
    print("Estado atual:", cursor.fetchall())
    
    print("\n2. Removendo o usuário de ID 2...")
    cursor.execute("DELETE FROM usuarios WHERE id = 2")
    conn.commit()
    
    cursor.execute("SELECT id, nome FROM usuarios")
    print("Estado atual (com lacuna):", cursor.fetchall())
    
    print("\n3. Simulando lógica de encontrar menor ID vago...")
    cursor.execute("SELECT id FROM usuarios ORDER BY id")
    ids_ocupados = {r[0] for r in cursor.fetchall()}
    id_vago = 1
    while id_vago in ids_ocupados:
        id_vago += 1
    print(f"Menor ID vago encontrado: {id_vago}")
    
    print(f"\n4. Cadastrando novo usuário no ID {id_vago}...")
    cursor.execute("INSERT INTO usuarios (id, nome, senha, reais, posicao) VALUES (?, ?, ?, ?, ?)", 
                   (id_vago, "NovoUser", "123", 100, id_vago))
    conn.commit()
    
    cursor.execute("SELECT id, nome FROM usuarios ORDER BY id")
    print("Estado final (lacuna preenchida):", cursor.fetchall())
    
    conn.close()

if __name__ == "__main__":
    testar_reutilizacao()
