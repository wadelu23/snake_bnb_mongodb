import services.data_service as svc

active_account = None


def reload_account():
    global active_account
    if not active_account:
        return

    active_account = svc.find_account_by_email(active_account.email)
    
def remind_login_msg(next_action:str) -> str:
    """remind user need login first for next action

    Args:
        next_action (str): an action

    Returns:
        str: complete sentence
    """
    return f'You must login first to {next_action}.'
