class UserAgent:
    
    _filename: str
    _user_agent: str

    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._read_user_agent()

    def _read_user_agent(self) -> None:
        self._user_agent = open(self._filename, "r").readline()

    def get_user_agent(self) -> str:
        return self._user_agent