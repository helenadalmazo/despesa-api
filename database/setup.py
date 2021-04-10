from database.repository import ExpenseCategoryRepository


def setup_data():
    groups = {
        "Alimentação": [
            "Mercado",
            "Restaurantes",
        ],
        "Educação": [
            "Escola",
            "Materiais",
        ],
        "Entretenimento": [
            "Eventos",
            "Filmes",
            "Jogos",
            "Viagens",
        ],
        "Moradia": [
            "Aluguel",
            "Eletrônicos",
            "Manutenção",
            "Móveis",
        ],
        "Saúde": [
            "Despesas médicas",
            "Farmácia",
        ],
        "Serviços": [
            "Água",
            "Eletricidade",
            "Gás",
            "Impostos",
            "TV/Telefone/Internet",
        ],
        "Transporte": [
            "Avião",
            "Bicicleta",
            "Carro",
            "Combustível",
            "Estacionamento",
            "Seguro",
            "Táxi",
            "Transporte público",
        ],
        "Outros": [
            "Outros",
        ]
    }

    expense_category_repository = ExpenseCategoryRepository()

    for group, names in groups.items():
        for name in names:
            expense_category = expense_category_repository.get_by_group_and_name(group, name)
            if not expense_category:
                print(f"Criando categoria de despesa. Grupo: {group}, Nome {name}")
                expense_category_repository.save(group, name)
