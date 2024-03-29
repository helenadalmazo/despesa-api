from exception.exception import ForbiddenException, ValidationException


def check_permission(user, group, permission_expected):
    permission = group.get_user_role(user)

    has_permission = permission in permission_expected

    if not has_permission:
        raise ForbiddenException()


def validate_params(params_received, params_to_validate, key_path=None):
    errors = []

    if not params_received:
        params_received = {}

    if key_path:
        params_received = params_received[key_path]

    if not params_received:
        params_received = {}

    if isinstance(params_received, list):
        for index, param_received in enumerate(params_received):
            for param in params_to_validate:
                if param not in param_received:
                    if key_path:
                        errors.append(f"O parâmetro [{key_path}[{index}].{param}] é obrigatório.")
                    else:
                        errors.append(f"O parâmetro [[{index}].{param}] é obrigatório.")

    if isinstance(params_received, dict):
        for param in params_to_validate:
            if param not in params_received:
                if key_path:
                    errors.append(f"O parâmetro [{key_path}.{param}] é obrigatório.")
                else:
                    errors.append(f"O parâmetro [{param}] é obrigatório.")

    if len(errors) > 0:
        raise ValidationException("Não foi possível processar essa requisição.", errors)


def parse_params(params_received, params_to_parse):
    data = {}

    for param in params_to_parse:
        if param in params_received:
            data[param] = params_received[param]

    return data
