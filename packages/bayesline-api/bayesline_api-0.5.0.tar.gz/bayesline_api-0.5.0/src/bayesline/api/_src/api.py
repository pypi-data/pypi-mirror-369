import abc

from bayesline.api._src.equity.api import AsyncBayeslineEquityApi, BayeslineEquityApi
from bayesline.api._src.permissions import AsyncUserPermissionsApi, UserPermissionsApi
from bayesline.api._src.tasks import AsyncTasksApi, TasksApi


class BayeslineApi(abc.ABC):

    @property
    @abc.abstractmethod
    def equity(self) -> BayeslineEquityApi: ...

    @property
    @abc.abstractmethod
    def permissions(self) -> UserPermissionsApi: ...

    @property
    @abc.abstractmethod
    def tasks(self) -> TasksApi: ...


class AsyncBayeslineApi(abc.ABC):

    @property
    @abc.abstractmethod
    def equity(self) -> AsyncBayeslineEquityApi: ...

    @property
    @abc.abstractmethod
    def permissions(self) -> AsyncUserPermissionsApi: ...

    @property
    @abc.abstractmethod
    def tasks(self) -> AsyncTasksApi: ...
