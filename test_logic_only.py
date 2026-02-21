from decimal import Decimal, ROUND_HALF_UP

def test_logic():
    print("--- Testando Lógica de Centavos (Simulação) ---")
    
    # 1. Simulação de Criação de Sala com valor quebrado
    saldo_inicial = Decimal("100.57")
    valor_sala = Decimal("50.25")
    
    # Lógica do código: valor_necessario = (valor_inicial / 2).quantize(0.01)
    valor_necessario = (valor_sala / Decimal('2')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    saldo_apos_criacao = saldo_inicial - valor_necessario
    print(f"Saldo Inicial: {saldo_inicial}")
    print(f"Valor da Sala: {valor_sala}")
    print(f"Valor descontado (50%): {valor_necessario}")
    print(f"Saldo após criação: {saldo_apos_criacao}")
    
    # 2. Simulação de Reembolso na Exclusão
    # Lógica do código: valor_reembolso = (valor_inicial / 2).quantize(0.01)
    valor_reembolso = (valor_sala / Decimal('2')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    saldo_apos_reembolso = saldo_apos_criacao + valor_reembolso
    
    print(f"Valor Reembolsado: {valor_reembolso}")
    print(f"Saldo após reembolso: {saldo_apos_reembolso}")
    
    if saldo_apos_reembolso == saldo_inicial:
        print("✅ SUCESSO: O saldo voltou exatamente ao valor original com centavos.")
    else:
        print(f"❌ FALHA: Diferença detectada! Original: {saldo_inicial}, Final: {saldo_apos_reembolso}")

    # 3. Simulação de Contabilidade de Vitória
    print("\n--- Testando Lógica de Vitória (Simulação) ---")
    valor_inicial = Decimal("33.33")
    porcentagem_casa = Decimal("10")
    
    valor_casa = (valor_inicial * (porcentagem_casa / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    premio = valor_inicial - valor_casa
    
    print(f"Valor Total em Jogo: {valor_inicial}")
    print(f"Taxa da Casa ({porcentagem_casa}%): {valor_casa}")
    print(f"Prêmio Líquido: {premio}")
    print(f"Soma (Casa + Prêmio): {valor_casa + premio}")
    
    if valor_casa + premio == valor_inicial:
        print("✅ SUCESSO: A contabilidade fechou perfeitamente em 100% do valor.")
    else:
        print(f"❌ AVISO: A contabilidade teve um desvio de {valor_inicial - (valor_casa + premio)}")

if __name__ == "__main__":
    test_logic()
