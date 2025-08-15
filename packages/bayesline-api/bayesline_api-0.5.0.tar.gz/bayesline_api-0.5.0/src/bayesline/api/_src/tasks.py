import abc
import enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", covariant=True)


class TaskResponse(BaseModel):
    task_id: str
    extra: dict[str, Any] = Field(default_factory=dict)


class TaskState(str, enum.Enum):
    """
    The state of a task.
    """

    CANCELLED = "CANCELLED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRY = "RETRY"


class TaskError(Exception): ...


class TaskProgress(BaseModel):
    """
    The progress of a task.
    """

    state: TaskState
    last_progress: int
    last_message: str
    last_context: str = ""


class Task(abc.ABC, Generic[T]):
    """
    Abstract base class representing a task that produces a result of type T.

    A task has a unique ID and can be in various states (queued, running, completed, etc).
    The task's progress can be monitored and its result retrieved once complete.
    """

    @property
    @abc.abstractmethod
    def task_id(self) -> str:
        """
        Returns
        -------
        str
            The unique identifier for this task.
        """

    @abc.abstractmethod
    def get_progress(self) -> TaskProgress:
        """
        Get the current progress status of the task.

        Returns
        -------
        TaskProgress
            The current progress status, containing information about
            completion percentage and status message.
        """

    @abc.abstractmethod
    def is_ready(self) -> bool:
        """
        Check if the task has completed and the result is ready.

        Returns
        -------
        bool
            True if the task is complete and result can be retrieved, False otherwise.
        """

    @abc.abstractmethod
    def get_result(self) -> T:
        """
        Get the result of the completed task.

        Returns
        -------
        T
            The result of the task.

        Raises
        ------
        TaskError
            If the task failed or is not yet complete.
        """

    @abc.abstractmethod
    def wait_result(self, timeout: float = -1.0, check_interval: float = 0.5) -> T:
        """
        Wait for the task to complete and return its result.

        Parameters
        ----------
        timeout: float, default=-1.0
            Maximum time in seconds to wait for completion.
            A negative value means wait indefinitely.
        check_interval: float, default=0.5
            Time in seconds between status checks.

        Returns
        -------
        T
            The result of the task.

        Raises
        ------
        TaskError
            If the task failed or timed out.
        """

    @abc.abstractmethod
    def wait_ready(self, timeout: float = -1.0, check_interval: float = 1.0) -> None:
        """
        Wait for the task to be ready.

        Parameters
        ----------
        timeout: float, default=-1.0
            Maximum time in seconds to wait for completion.
            A negative value means wait indefinitely.
        check_interval: float, default=0.5
            Time in seconds between status checks.

        Raises
        ------
        TaskError
            If the task failed or timed out.
        """

    @abc.abstractmethod
    def cancel(self) -> None:
        """
        Cancel the task.
        """


class AsyncTask(abc.ABC, Generic[T]):
    """
    Abstract base class representing a task that produces a result of type T.

    A task has a unique ID and can be in various states (queued, running, completed, etc).
    The task's progress can be monitored and its result retrieved once complete.
    """

    @property
    @abc.abstractmethod
    def task_id(self) -> str:
        """
        Returns
        -------
        str
            The unique identifier for this task.
        """

    @abc.abstractmethod
    async def get_progress(self) -> TaskProgress:
        """
        Get the current progress status of the task.

        Returns
        -------
        TaskProgress
            The current progress status, containing information about
            completion percentage and status message.
        """

    @abc.abstractmethod
    async def is_ready(self) -> bool:
        """
        Check if the task has completed and the result is ready.

        Returns
        -------
        bool
            True if the task is complete and result can be retrieved, False otherwise.
        """

    @abc.abstractmethod
    async def get_result(self) -> T:
        """
        Get the result of the completed task.

        Returns
        -------
        T
            The result of the task.

        Raises
        ------
        TaskError
            If the task failed or is not yet complete.
        """

    @abc.abstractmethod
    async def wait_result(
        self, timeout: float = -1.0, check_interval: float = 1.0
    ) -> T:
        """
        Wait for the task to complete and return its result.

        Parameters
        ----------
        timeout: float, default=-1.0
            Maximum time in seconds to wait for completion.
            A negative value means wait indefinitely.
        check_interval: float, default=0.5
            Time in seconds between status checks.

        Returns
        -------
        T
            The result of the task.

        Raises
        ------
        TaskError
            If the task failed or timed out.
        """

    @abc.abstractmethod
    async def wait_ready(
        self, timeout: float = -1.0, check_interval: float = 1.0
    ) -> None:
        """
        Wait for the task to be ready.

        Parameters
        ----------
        timeout: float, default=-1.0
            Maximum time in seconds to wait for completion.
            A negative value means wait indefinitely.
        check_interval: float, default=0.5
            Time in seconds between status checks.

        Raises
        ------
        TaskError
            If the task failed or timed out.
        """

    @abc.abstractmethod
    async def cancel(self) -> None:
        """
        Cancel the task.
        """


class TasksApi(abc.ABC):

    @abc.abstractmethod
    def get_task_progress(self, task_id: str) -> TaskProgress:
        """
        Get the progress of a task if it exists.

        Parameters
        ----------
        task_id: str
            The ID of the task.

        Raises
        ------
        KeyError
            If the task does not exist.

        Returns
        -------
        TaskProgress
            The progress of the task.
        """


class AsyncTasksApi(abc.ABC):

    @abc.abstractmethod
    async def get_task_progress(self, task_id: str) -> TaskProgress:
        """
        Get the progress of a task if it exists.

        Parameters
        ----------
        task_id: str
            The ID of the task.

        Raises
        ------
        KeyError
            If the task does not exist.

        Returns
        -------
        TaskProgress
            The progress of the task.
        """
