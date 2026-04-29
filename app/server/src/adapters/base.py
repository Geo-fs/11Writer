from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class Adapter(ABC, Generic[T]):
    source_name: str

    @abstractmethod
    async def fetch(self) -> T:
        raise NotImplementedError

