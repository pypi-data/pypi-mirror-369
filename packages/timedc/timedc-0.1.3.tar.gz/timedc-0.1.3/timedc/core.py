import time

__all__ = ["getTime"]

UNITS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
}

VALID_FORMATS = {"t", "T", "d", "D", "f", "F", "R"}

def getTime(duration: str, fmt: str = "") -> str:
    """
    Генерация Discord timestamp.

    :param duration: строка с временем (например "10m", "2h", "3d")
    :param fmt: формат отображения ("t", "T", "d", "D", "f", "F", "R" или "")
    :return: строка вида <t:UNIX:fmt>
    """
    if len(duration) < 2:
        raise ValueError("Неверный формат времени, пример: 10m, 2h, 3d")

    value, unit = duration[:-1], duration[-1]

    if not value.isdigit() or unit not in UNITS:
        raise ValueError(f"Неверный ввод: {duration}")

    seconds = int(value) * UNITS[unit]
    unix_time = int(time.time()) + seconds

    if fmt and fmt not in VALID_FORMATS:
        raise ValueError(f"Неверный формат отображения: {fmt}")

    return f"<t:{unix_time}{':' + fmt if fmt else ''}>"
