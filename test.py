def test(string: list, a: str) -> str:
    for s in string:
        if s == a:
            return True
    return False


r = test(string="qwerty", a="i")
print(r)
