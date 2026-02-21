import sys
import os
from decimal import Decimal, ROUND_HALF_UP

# Adicionar o diretório atual ao sys.path para importar o backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database_config import executar_query_commit, executar_query_fetchall

def setup_test_data():
    print("--- Configurando dados de teste ---")
    # Limpar dados antigos (opcional, mas cuidado se for banco real)
    # executar_query_commit("DELETE FROM salas")
    # executar_query_commit("DELETE FROM usuarios WHERE nome LIKE 'TestUser%'")
    
    # Criar usuário de teste com saldo quebrado
    nome = "TestUserCentavos"
    senha = "password"
    reais = Decimal("100.57")
    whatsapp = "11999999999"
    
    # Remover se já existir
    executar_query_commit("DELETE FROM usuarios WHERE nome = %s", (nome,))
    
    executar_query_commit(
        "INSERT INTO usuarios (nome, senha, reais, whatsapp) VALUES (%s, %s, %s, %s)",
        (nome, senha, float(reais), whatsapp)
    )
    
    user = executar_query_fetchall("SELECT id, reais FROM usuarios WHERE nome = %s", (nome,))
    print(f"Usuário criado: {nome}, Saldo: {user[0][1]}")
    return user[0][0], user[0][1]

def test_criacao_e_exclusao_sala(user_id, saldo_inicial):
    print("\n--- Testando Criação e Exclusão de Sala (Reembolso) ---")
    nome_sala = "Sala Centavos Test"
    valor_inicial = Decimal("50.25")
    criador = "TestUserCentavos"
    
    # 1. Criar Sala
    # No código, ao criar sala, desconta metade do valor_inicial
    valor_necessario = (valor_inicial / Decimal('2')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    print(f"Valor da sala: {valor_inicial}, Valor descontado (50%): {valor_necessario}")
    
    executar_query_commit(
        "INSERT INTO salas (nome_sala, valor_inicial, criador, jogadores, status) VALUES (%s, %s, %s, %s, %s)",
        (nome_sala, valor_inicial, criador, str(user_id), 'aberta')
    )
    
    # Simular o desconto no saldo (como no salas.py)
    novo_saldo = saldo_inicial - valor_necessario
    executar_query_commit("UPDATE usuarios SET reais = %s WHERE id = %s", (float(novo_saldo), user_id))
    
    # Verificar saldo após criação
    res = executar_query_fetchall("SELECT reais FROM usuarios WHERE id = %s", (user_id,))
    saldo_pos_criacao = res[0][0]
    print(f"Saldo após criar sala: {saldo_pos_criacao} (Esperado: {novo_saldo})")
    
    # Obter ID da sala
    res_sala = executar_query_fetchall("SELECT id_sala FROM salas WHERE nome_sala = %s", (nome_sala,))
    id_sala = res_sala[0][0]
    
    # 2. Excluir Sala (Reembolso)
    print(f"Excluindo sala #{id_sala}...")
    
    # Lógica do salas.py para exclusão
    sala = executar_query_fetchall("SELECT valor_inicial, jogadores, status, vencedor_id FROM salas WHERE id_sala = %s", (id_sala,))
    v_inicial = Decimal(str(sala[0][0]))
    j_str = sala[0][1]
    status = sala[0][2]
    vencedor_id = sala[0][3]
    
    j_ids = [j.strip() for j in j_str.split(",") if j.strip()]
    num_jogadores = len(j_ids)
    
    if status != 'finalizada' and vencedor_id is None:
        valor_reembolso = (v_inicial / Decimal('2')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        print(f"Valor a reembolsar por jogador: {valor_reembolso}")
        for j_id in j_ids:
            executar_query_commit("UPDATE usuarios SET reais = reais + %s WHERE id = %s", (float(valor_reembolso), int(j_id)))
            
    executar_query_commit("DELETE FROM salas WHERE id_sala = %s", (id_sala,))
    
    # Verificar saldo após exclusão
    res = executar_query_fetchall("SELECT reais FROM usuarios WHERE id = %s", (user_id,))
    saldo_final = res[0][0]
    print(f"Saldo após excluir sala (reembolsado): {saldo_final} (Esperado: {saldo_inicial})")
    
    if saldo_final == saldo_inicial:
        print("SUCESSO: Reembolso de centavos funcionou perfeitamente!")
    else:
        print(f"FALHA: Saldo final {saldo_final} diferente do inicial {saldo_inicial}")

def test_contabilidade_vitoria():
    print("\n--- Testando Contabilidade de Vitória com Centavos ---")
    # Criar dois jogadores
    executar_query_commit("DELETE FROM usuarios WHERE nome IN ('Player1', 'Player2')")
    executar_query_commit("INSERT INTO usuarios (nome, senha, reais) VALUES ('Player1', 'pass', 100.00), ('Player2', 'pass', 100.00)")
    
    p1 = executar_query_fetchall("SELECT id FROM usuarios WHERE nome = 'Player1'")[0][0]
    p2 = executar_query_fetchall("SELECT id FROM usuarios WHERE nome = 'Player2'")[0][0]
    
    valor_inicial = Decimal("33.33") # Valor quebrado
    nome_sala = "Sala Competição"
    
    # Criar sala e adicionar jogadores
    executar_query_commit(
        "INSERT INTO salas (nome_sala, valor_inicial, criador, jogadores, status) VALUES (%s, %s, %s, %s, %s)",
        (nome_sala, valor_inicial, 'Player1', f"{p1},{p2}", 'aberta')
    )
    
    res_sala = executar_query_fetchall("SELECT id_sala FROM salas WHERE nome_sala = %s", (nome_sala,))
    id_sala = res_sala[0][0]
    
    # Simular definição de ganhador (lógica do salas.py)
    vencedor_id = p1
    porcentagem_casa = Decimal('10')
    
    valor_casa = (valor_inicial * (porcentagem_casa / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    premio = valor_inicial - valor_casa
    
    print(f"Valor Inicial: {valor_inicial}")
    print(f"Taxa da Casa (10%): {valor_casa}")
    print(f"Prêmio do Vencedor: {premio}")
    
    # Verificar se a soma bate
    if valor_casa + premio == valor_inicial:
        print("Soma (Casa + Prêmio) bate com Valor Inicial!")
    else:
        print(f"AVISO: Soma {valor_casa + premio} difere de {valor_inicial}")

    # Atualizar no DB
    executar_query_commit("UPDATE usuarios SET reais = reais + %s WHERE id = %s", (float(premio), vencedor_id))
    
    # Verificar saldo final do vencedor
    res_vencedor = executar_query_fetchall("SELECT reais FROM usuarios WHERE id = %s", (vencedor_id,))
    print(f"Saldo final do vencedor: {res_vencedor[0][0]}")
    
    # Limpeza
    executar_query_commit("DELETE FROM salas WHERE id_sala = %s", (id_sala,))
    executar_query_commit("DELETE FROM usuarios WHERE nome IN ('Player1', 'Player2')")

if __name__ == "__main__":
    try:
        uid, saldo = setup_test_data()
        test_criacao_e_exclusao_sala(uid, saldo)
        test_contabilidade_vitoria()
    except Exception as e:
        print(f"Erro durante os testes: {e}")
