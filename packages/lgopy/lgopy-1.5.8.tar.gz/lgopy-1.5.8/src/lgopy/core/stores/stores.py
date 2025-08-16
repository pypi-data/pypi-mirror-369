from abc import ABC, abstractmethod
from typing import Any, Dict, Union
from io import BytesIO
from pathlib import Path


class BaseMetadataStore(ABC):
    """Abstract base class for a metadata store."""

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def all(self) -> Dict[str, Any]:
        pass


class BaseArtifactStore(ABC):
    """Abstract base class for an artifact store."""

    @abstractmethod
    def save(self, key: str, data: Union[str, bytes, Path]) -> None:
        pass

    @abstractmethod
    def load(self, key: str) -> Union[str, bytes, None]:
        pass

    @abstractmethod
    def as_bytes_io(self, key: str) -> BytesIO:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def all(self) -> Dict[str, Union[str, bytes]]:
        pass

class InMemoryArtifactStore(BaseArtifactStore):
    def __init__(self):
        self._store: Dict[str, Union[str, bytes]] = {}

    def save(self, key: str, data: Union[str, bytes, Path]) -> None:
        if isinstance(data, Path) or (isinstance(data, str) and Path(data).exists()):
            path = Path(data)
            with path.open("rb") as f:
                content = f.read()
            self._store[key] = content
        else:
            self._store[key] = data

    def load(self, key: str) -> Union[str, bytes, None]:
        return self._store.get(key)

    def as_bytes_io(self, key: str) -> BytesIO:
        data = self._store.get(key)
        if isinstance(data, bytes):
            return BytesIO(data)
        elif isinstance(data, str):
            return BytesIO(data.encode("utf-8"))
        raise TypeError(f"Artifact '{key}' is not str or bytes.")

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    def all(self) -> Dict[str, Union[str, bytes]]:
        return dict(self._store)


class InMemoryMetadataStore(BaseMetadataStore):
    def __init__(self):
        self._store: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    def all(self) -> Dict[str, Any]:
        return dict(self._store)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __delitem__(self, key: str) -> None:
        self.delete(key)

    def __contains__(self, key: str) -> bool:
        return key in self._store

    def __len__(self) -> int:
        return len(self._store)

    def __str__(self):
        return f"InMemoryMetadataStore({self._store})"

