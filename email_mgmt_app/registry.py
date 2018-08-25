class AppSubRegistry:
    def __init__(self) -> None:
        self._mappers = {}
        pass

    @property
    def mappers(self) -> dict:
        return self._mappers



