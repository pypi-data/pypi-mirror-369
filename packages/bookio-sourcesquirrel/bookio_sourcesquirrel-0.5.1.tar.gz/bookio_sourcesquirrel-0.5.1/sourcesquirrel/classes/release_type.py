from uuid import UUID

from sourcesquirrel.helpers import required


class ReleaseType:
    def __init__(self, id: UUID, name: str, emoji: str):
        self.id: UUID = id
        self.name: str = name
        self.emoji: str = emoji

    def verify(self):
        required("release_type.name", self.name, str)
        required("release_type.emoji", self.emoji, str)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.emoji} {self.name}"
