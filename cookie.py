class Cookie:

    _filename: str
    _cookie: dict

    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._read_cookie()

    def _read_cookie(self) -> None:
        lst = open(self._filename, "r").readline().split("; ")
        for i in range(len(lst)):
            lst[i] = lst[i].split("=")
        self._cookie = {elm[0]: elm[1] for elm in lst}

    def get_cookie(self) -> dict:
        return self._cookie