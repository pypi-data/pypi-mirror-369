from typing import (
    Any,
    Callable,
    ParamSpec,
    TypeVar,
    overload,
    Coroutine,
    Iterable,
    AsyncIterable,
    Protocol,
    Generic,
)

# Public API re-exports (for type checkers)
from .errors import CommandError, ToolError, ConfigurationError

P = ParamSpec("P")
T_co = TypeVar("T_co", covariant=True)

class SyncCommandFn(Protocol, Generic[P, T_co]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T_co: ...
    def stream(self, *args: P.args, **kwargs: P.kwargs) -> Iterable[str]: ...
    def async_(self, *args: P.args, **kwargs: P.kwargs) -> Coroutine[Any, Any, T_co]: ...

class AsyncCommandFn(Protocol, Generic[P, T_co]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Coroutine[Any, Any, T_co]: ...
    def stream(self, *args: P.args, **kwargs: P.kwargs) -> AsyncIterable[str]: ...
    def async_(self, *args: P.args, **kwargs: P.kwargs) -> Coroutine[Any, Any, T_co]: ...

# Decorator protocol returning appropriate wrapper based on function type
class _CommandDecorator(Protocol, Generic[T_co]):
    @overload
    def __call__(self, __func: Callable[P, str], /) -> SyncCommandFn[P, T_co]: ...
    @overload
    def __call__(
        self, __func: Callable[P, Coroutine[Any, Any, str]], /
    ) -> AsyncCommandFn[P, T_co]: ...

# Decorator overloads for sync/async
# Explicit output type
@overload
def command(
    __func: Callable[P, str],
    /,
    *,
    output: type[T_co],
    tools: list[Callable[..., Any]] | None = ...,
    model: str | None = ...,
    temperature: float | None = ...,
    max_tokens: int | None = ...,
    system: str | None = ...,
    retry: int | None = ...,
    retry_on: type[BaseException] | None = ...,
) -> SyncCommandFn[P, T_co]: ...
@overload
def command(
    __func: Callable[P, Coroutine[Any, Any, str]],
    /,
    *,
    output: type[T_co],
    tools: list[Callable[..., Any]] | None = ...,
    model: str | None = ...,
    temperature: float | None = ...,
    max_tokens: int | None = ...,
    system: str | None = ...,
    retry: int | None = ...,
    retry_on: type[BaseException] | None = ...,
) -> AsyncCommandFn[P, T_co]: ...

# Output omitted (defaults to str)
@overload
def command(
    __func: Callable[P, str],
    /,
    *,
    output: None = ...,
    tools: list[Callable[..., Any]] | None = ...,
    model: str | None = ...,
    temperature: float | None = ...,
    max_tokens: int | None = ...,
    system: str | None = ...,
    retry: int | None = ...,
    retry_on: type[BaseException] | None = ...,
) -> SyncCommandFn[P, str]: ...
@overload
def command(
    __func: Callable[P, Coroutine[Any, Any, str]],
    /,
    *,
    output: None = ...,
    tools: list[Callable[..., Any]] | None = ...,
    model: str | None = ...,
    temperature: float | None = ...,
    max_tokens: int | None = ...,
    system: str | None = ...,
    retry: int | None = ...,
    retry_on: type[BaseException] | None = ...,
) -> AsyncCommandFn[P, str]: ...

# Decorator factory (called as @command(...))
@overload
def command(
    *,
    output: type[T_co],
    tools: list[Callable[..., Any]] | None = ...,
    model: str | None = ...,
    temperature: float | None = ...,
    max_tokens: int | None = ...,
    system: str | None = ...,
    retry: int | None = ...,
    retry_on: type[BaseException] | None = ...,
) -> _CommandDecorator[T_co]: ...
@overload
def command(
    *,
    output: None = ...,
    tools: list[Callable[..., Any]] | None = ...,
    model: str | None = ...,
    temperature: float | None = ...,
    max_tokens: int | None = ...,
    system: str | None = ...,
    retry: int | None = ...,
    retry_on: type[BaseException] | None = ...,
) -> _CommandDecorator[str]: ...

class _AskNamespace:
    def __call__(
        self,
        prompt: str,
        *,
        tools: list[Callable[..., Any]] | None = ...,
        context: dict[str, Any] | None = ...,
        **overrides: Any,
    ) -> str: ...
    def stream(
        self,
        prompt: str,
        *,
        tools: list[Callable[..., Any]] | None = ...,
        context: dict[str, Any] | None = ...,
        **overrides: Any,
    ) -> Iterable[str]: ...
    def stream_async(
        self,
        prompt: str,
        *,
        tools: list[Callable[..., Any]] | None = ...,
        context: dict[str, Any] | None = ...,
        **overrides: Any,
    ) -> AsyncIterable[str]: ...

# Runtime values provided by the package
def tool(__func: Callable[..., Any] | None = ..., /, **kwargs: Any) -> Any: ...
def require(
    predicate: Callable[[Any], bool], message: str
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def ensure(
    predicate: Callable[[Any], bool], message: str
) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def configure(**kwargs: Any) -> None: ...

# Implementation provided at runtime
ask: _AskNamespace

__all__ = [
    "command",
    "tool",
    "require",
    "ensure",
    "ask",
    "configure",
    "CommandError",
    "ToolError",
    "ConfigurationError",
]
