import contextlib
import enum
import inspect
import typing

from modern_di import Container
from modern_di.providers.abstract import AbstractCreatorProvider


T_co = typing.TypeVar("T_co", covariant=True)
P = typing.ParamSpec("P")


class Resource(AbstractCreatorProvider[T_co]):
    __slots__ = [*AbstractCreatorProvider.BASE_SLOTS, "_is_async"]

    def _is_creator_async(
        self,
        _: contextlib.AbstractContextManager[T_co] | contextlib.AbstractAsyncContextManager[T_co],
    ) -> typing.TypeGuard[contextlib.AbstractAsyncContextManager[T_co]]:
        return self._is_async

    def __init__(
        self,
        scope: enum.IntEnum,
        creator: typing.Callable[
            P,
            typing.Iterator[T_co]
            | typing.AsyncIterator[T_co]
            | typing.ContextManager[T_co]
            | typing.AsyncContextManager[T_co],
        ],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        new_creator: typing.Any
        if inspect.isasyncgenfunction(creator):
            self._is_async = True
            new_creator = contextlib.asynccontextmanager(creator)
        elif inspect.isgeneratorfunction(creator):
            self._is_async = False
            new_creator = contextlib.contextmanager(creator)
        elif isinstance(creator, type) and issubclass(creator, typing.AsyncContextManager):
            self._is_async = True
            new_creator = creator
        elif isinstance(creator, type) and issubclass(creator, typing.ContextManager):
            self._is_async = False
            new_creator = creator
        else:
            msg = "Unsupported resource type"
            raise TypeError(msg)

        super().__init__(scope, new_creator, *args, **kwargs)

    async def async_resolve(self, container: Container) -> T_co:
        container = container.find_container(self.scope)
        if (override := container.fetch_override(self.provider_id)) is not None:
            return typing.cast(T_co, override)

        provider_state = container.fetch_provider_state(
            self.provider_id, is_async_resource=self._is_async, use_asyncio_lock=True
        )
        if provider_state.instance is not None:
            return typing.cast(T_co, provider_state.instance)

        if provider_state.asyncio_lock:
            await provider_state.asyncio_lock.acquire()

        try:
            if provider_state.instance is not None:
                return typing.cast(T_co, provider_state.instance)

            _intermediate_ = await self._async_build_creator(container)

            if self._is_creator_async(self._creator):  # type: ignore[arg-type]
                provider_state.context_stack = contextlib.AsyncExitStack()
                provider_state.instance = await provider_state.context_stack.enter_async_context(_intermediate_)
            else:
                provider_state.context_stack = contextlib.ExitStack()
                provider_state.instance = provider_state.context_stack.enter_context(_intermediate_)
        finally:
            if provider_state.asyncio_lock:
                provider_state.asyncio_lock.release()

        return typing.cast(T_co, provider_state.instance)

    def sync_resolve(self, container: Container) -> T_co:
        container = container.find_container(self.scope)
        if (override := container.fetch_override(self.provider_id)) is not None:
            return typing.cast(T_co, override)

        provider_state = container.fetch_provider_state(
            self.provider_id, is_async_resource=self._is_async, use_threading_lock=True
        )
        if provider_state.instance is not None:
            return typing.cast(T_co, provider_state.instance)

        if self._is_async:
            msg = "Async resource cannot be resolved synchronously"
            raise RuntimeError(msg)

        if provider_state.threading_lock:
            provider_state.threading_lock.acquire()

        try:
            if provider_state.instance is not None:
                return typing.cast(T_co, provider_state.instance)

            _intermediate_ = self._sync_build_creator(container)

            provider_state.context_stack = contextlib.ExitStack()
            provider_state.instance = provider_state.context_stack.enter_context(
                typing.cast(contextlib.AbstractContextManager[typing.Any], _intermediate_)
            )
        finally:
            if provider_state.threading_lock:
                provider_state.threading_lock.release()

        return typing.cast(T_co, provider_state.instance)
