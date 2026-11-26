import re

MONTH_PATTERN = re.compile(r"[0-9]{4}-(0[1-9]|1[0-2])")


def check_month(text):
    """校验报表月份格式：YYYY-MM（如 2026-11）。
    返回 (True, "") 或 (False, 具体原因)。
    """
    if not isinstance(text, str):
        return False, f"月份必须是字符串，现在是 {type(text).__name__}"

    s = text.strip()

    if not s:
        return False, "月份不能为空"

    if MONTH_PATTERN.fullmatch(s):
        return True, ""

    # 走到这里说明不合法，逐层找原因，给具体提示
    if not s.isascii():
        return False, "只能使用半角数字和半角短横线，例：2026-11"

    if len(s) != 7:
        return False, f"应为 YYYY-MM 共 7 个字符，现在是 {len(s)} 个：{s!r}"

    if s[4] != "-":
        return False, f"年月之间要用 - 连接，现在第 5 个字符是 {s[4]!r}"

    if not s[:4].isdigit():
        return False, f"年份必须是 4 位数字，现在是 {s[:4]!r}"

    if not s[5:].isdigit():
        return False, f"月份必须是 2 位数字，现在是 {s[5:]!r}"

    if not (1 <= int(s[5:]) <= 12):
        return False, f"月份只能在 01~12 之间，现在是 {s[5:]}"

    return False, f"格式应为 YYYY-MM，例如 2026-11，现在是 {s!r}"
