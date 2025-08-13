_timer_enabled = False  # Variable globale pour déterminer si le timer est actif ou non

def set_timer(state: bool):
    """
    Active ou désactive le timer
    :param state: détermine l'état du timer
    """
    global _timer_enabled
    _timer_enabled = state


def get_timer() -> bool:
    """
    récupère l'état du timer
    :return: l'état du timer
    """
    return _timer_enabled
