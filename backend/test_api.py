import requests

BASE_URL = "https://5000-ig29be28rj7ol9qi77gi6-c9a2ba3b.manusvm.computer/api"

def test_criar_usuario(nome, senha, reais, whatsapp):
    url = f"{BASE_URL}/usuarios"
    data = {"nome": nome, "senha": senha, "reais": reais, "whatsapp": whatsapp}
    response = requests.post(url, json=data)
    print(f"Criar Usuário {nome}: Status Code: {response.status_code}, Response: {response.text}")
    return response.json()

def test_listar_usuarios():
    url = f"{BASE_URL}/usuarios"
    response = requests.get(url)
    print(f"Listar Usuários: Status Code: {response.status_code}, Response: {response.text}")
    return response.json()

def test_criar_sala(nome_sala, valor_inicial, criador, whatsapp):
    url = f"{BASE_URL}/salas"
    data = {"nome_sala": nome_sala, "valor_inicial": valor_inicial, "criador": criador, "whatsapp": whatsapp}
    response = requests.post(url, json=data)
    print(f"Criar Sala {nome_sala}: Status Code: {response.status_code}, Response: {response.text}")
    return response.json()

def test_entrar_em_sala(id_sala, id_usuario, nome_usuario):
    url = f"{BASE_URL}/salas/{id_sala}/entrar"
    data = {"id_usuario": id_usuario, "nome_usuario": nome_usuario}
    response = requests.post(url, json=data)
    print(f"Entrar na Sala {id_sala} (Usuário {nome_usuario}): Status Code: {response.status_code}, Response: {response.text}")
    return response.json()

def test_obter_jogadores_sala(id_sala):
    url = f"{BASE_URL}/salas/{id_sala}/jogadores"
    response = requests.get(url)
    print(f"Jogadores na Sala {id_sala}: Status Code: {response.status_code}, Response: {response.text}")
    return response.json()

if __name__ == "__main__":
    # Limpar o banco de dados antes dos testes (opcional, para garantir um estado limpo)
    # Isso exigiria uma rota de API para limpar o DB, que não está implementada aqui.
    # Para testes, pode ser necessário reiniciar o ambiente ou limpar o DB manualmente.

    # Teste 1: Criar usuários
    user1_data = test_criar_usuario("Jogador1", "senha123", 1000, "11999999991")
    user2_data = test_criar_usuario("Jogador2", "senha123", 1000, "11999999992")
    user3_data = test_criar_usuario("Jogador3", "senha123", 1000, "11999999993")

    # Listar usuários para obter IDs
    usuarios = test_listar_usuarios()
    jogador1_id = None
    jogador2_id = None
    jogador3_id = None
    for user in usuarios:
        if user["nome"] == "Jogador1":
            jogador1_id = user["id"]
        elif user["nome"] == "Jogador2":
            jogador2_id = user["id"]
        elif user["nome"] == "Jogador3":
            jogador3_id = user["id"]

    if jogador1_id and jogador2_id and jogador3_id:
        # Teste 2: Criar uma sala com Jogador1
        sala1_data = test_criar_sala("Sala Teste 1", 200, "Jogador1", "11999999991")
        sala1_id = None
        if "message" in sala1_data and "Sala Teste 1" in sala1_data["message"]:
            # Precisamos de uma forma de obter o ID da sala criada. Idealmente, a API retornaria o ID.
            # Por enquanto, vamos listar as salas e pegar a primeira.
            salas = requests.get(f"{BASE_URL}/salas").json()
            if salas:
                sala1_id = salas[0]["id_sala"]
                print(f"ID da Sala Teste 1: {sala1_id}")

        if sala1_id:
            # Teste 3: Jogador2 entra na Sala Teste 1
            test_entrar_em_sala(sala1_id, jogador2_id, "Jogador2")
            test_obter_jogadores_sala(sala1_id)

            # Teste 4: Jogador3 tenta entrar na Sala Teste 1 (deve falhar)
            test_entrar_em_sala(sala1_id, jogador3_id, "Jogador3")
            test_obter_jogadores_sala(sala1_id)

    else:
        print("Erro: Não foi possível obter os IDs dos jogadores.")


