from exception.exception import ValidationException


def validate_params(params_received, params_to_validate):
    errors = []

    for param in params_to_validate:
        if param not in params_received:
            errors.append(f"O parâmetro [{param}] é obrigatório.")

    if len(errors) > 0:
        raise ValidationException("Não foi possível processar essa requisição.", errors)


def parse_params(params_received, params_to_parse):
    data = {}

    for param in params_to_parse:
        if param in params_received:
            data[param] = params_received[param]

    return data
