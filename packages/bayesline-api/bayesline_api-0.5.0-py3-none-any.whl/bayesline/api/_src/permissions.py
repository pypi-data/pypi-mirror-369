import abc
from typing import Any


class AsyncUserPermissionsApi(abc.ABC):

    @abc.abstractmethod
    async def get_permissions_map(self) -> dict[str, Any]: ...

    @abc.abstractmethod
    async def get_perm(self, key: str, default: bool = True) -> Any: ...

    @abc.abstractmethod
    async def get_perms(
        self, keys: list[str], default: bool = True
    ) -> dict[str, Any]: ...


class UserPermissionsApi(abc.ABC):

    @abc.abstractmethod
    def get_permissions_map(self) -> dict[str, Any]: ...

    @abc.abstractmethod
    def get_perm(self, key: str, default: bool = True) -> Any: ...

    @abc.abstractmethod
    def get_perms(self, keys: list[str], default: bool = True) -> dict[str, Any]: ...
