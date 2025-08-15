from __future__ import annotations

import inspect
from collections.abc import Iterable
from typing import Any, Callable

import json as _json
from .config import get_config
from .errors import CommandError
from .models.base import get_backend
from .tool import ToolCallable, ToolSpec
from .types import to_json_schema, parse_output


def command(
    fn: Callable[..., Any] | None = None,
    *,
    output: type | None = None,
    tools: list[Callable[..., Any]] | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    system: str | None = None,
    retry: int | None = None,
    retry_on: type[BaseException] | None = None,
):
    """Decorator to declare an AI-powered command.

    The wrapped function returns an English specification (prompt). This
    decorator executes the model with optional tools and parses the result
    into the annotated return type.
    """

    def wrap(func: Callable[..., Any]):
        return Command(
            func,
            output_type=output or _get_return_type(func),
            tools=tools or [],
            per_command_cfg={
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "default_system": system,
                "retry": retry,
                "retry_on": retry_on,
            },
        )

    if fn is not None:
        return wrap(fn)
    return wrap


class Command:
    def __init__(
        self,
        func: Callable[..., Any],
        *,
        output_type: type | None,
        tools: list[Callable[..., Any]],
        per_command_cfg: dict[str, Any],
    ):
        self._func = func
        self._output_type = output_type
        self._tools = [
            t if isinstance(t, ToolCallable) else ToolCallable(_to_spec(t)) for t in tools
        ]
        self._cfg = {k: v for k, v in per_command_cfg.items() if v is not None}
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self._is_async = inspect.iscoroutinefunction(func)

    # Synchronous call
    def __call__(self, *args, **kwargs):
        if self._is_async:
            return self.async_(*args, **kwargs)
        prompt = self._func(*args, **kwargs)
        if not isinstance(prompt, str):
            prompt = str(prompt)
        prompt = _augment_prompt(prompt, self._output_type)
        effective = get_config(self._cfg)
        backend = get_backend(effective.model)

        output_schema = to_json_schema(self._output_type) if self._output_type else None

        attempts = max(int(effective.retry or 1), 1)
        last_err: Exception | None = None
        for _ in range(attempts):
            try:
                text = backend.complete(
                    prompt,
                    tools=self._tools or None,
                    output_schema=output_schema,
                    config=effective,
                )
                if self._output_type is None:
                    return text
                try:
                    return parse_output(self._output_type, text)
                except Exception as parse_exc:
                    expected = getattr(self._output_type, "__name__", str(self._output_type))
                    snippet = (
                        (text[:120] + "…") if isinstance(text, str) and len(text) > 120 else text
                    )
                    raise CommandError(
                        f"Failed to parse model output as {expected}: {snippet!r}"
                    ) from parse_exc
            except Exception as e:
                last_err = e
                if effective.retry_on and not isinstance(e, effective.retry_on):
                    break
                # else: retry
        # Exhausted retries
        if isinstance(last_err, CommandError):
            raise last_err
        raise CommandError(str(last_err) if last_err else "Unknown command error")

    def stream(
        self, *args, **kwargs
    ) -> Iterable[str] | Any:  # may return AsyncIterable for async commands
        effective = get_config(self._cfg)
        backend = get_backend(effective.model)
        output_schema = to_json_schema(self._output_type) if self._output_type else None

        if not self._is_async:
            prompt = self._func(*args, **kwargs)
            if not isinstance(prompt, str):
                prompt = str(prompt)
            try:
                return backend.stream(
                    prompt,
                    tools=self._tools or None,
                    output_schema=output_schema,
                    config=effective,
                )
            except Exception as e:
                raise CommandError(str(e)) from e

        async def agen():
            prompt_val = await self._func(*args, **kwargs)
            if not isinstance(prompt_val, str):
                prompt_str = str(prompt_val)
            else:
                prompt_str = prompt_val
            prompt_str = _augment_prompt(prompt_str, self._output_type)
            try:
                aiter = await backend.astream(
                    prompt_str,
                    tools=self._tools or None,
                    output_schema=output_schema,
                    config=effective,
                )
            except Exception as e:
                raise CommandError(str(e)) from e
            async for chunk in aiter:
                yield chunk

        return agen()

    async def async_(self, *args, **kwargs):  # pragma: no cover
        if self._is_async:
            prompt_val = await self._func(*args, **kwargs)
        else:
            prompt_val = self._func(*args, **kwargs)
        if not isinstance(prompt_val, str):
            prompt = str(prompt_val)
        else:
            prompt = prompt_val
        prompt = _augment_prompt(prompt, self._output_type)
        effective = get_config(self._cfg)
        backend = get_backend(effective.model)
        output_schema = to_json_schema(self._output_type) if self._output_type else None

        attempts = max(int(effective.retry or 1), 1)
        last_err: Exception | None = None
        for _ in range(attempts):
            try:
                text = await backend.acomplete(
                    prompt,
                    tools=self._tools or None,
                    output_schema=output_schema,
                    config=effective,
                )
                if self._output_type is None:
                    return text
                try:
                    return parse_output(self._output_type, text)
                except Exception as parse_exc:
                    expected = getattr(self._output_type, "__name__", str(self._output_type))
                    snippet = (
                        (text[:120] + "…") if isinstance(text, str) and len(text) > 120 else text
                    )
                    raise CommandError(
                        f"Failed to parse model output as {expected}: {snippet!r}"
                    ) from parse_exc
            except Exception as e:
                last_err = e
                if effective.retry_on and not isinstance(e, effective.retry_on):
                    break
        if isinstance(last_err, CommandError):
            raise last_err
        raise CommandError(str(last_err) if last_err else "Unknown command error")


def _to_spec(func: Callable[..., Any]) -> ToolSpec:
    # If already decorated with @tool, it exposes _alloy_tool_spec
    spec = getattr(func, "_alloy_tool_spec", None)
    if spec is not None:
        return spec
    # Otherwise, create a minimal spec
    from .tool import ToolSpec as TS
    import inspect as _inspect

    return TS(
        func=func,
        name=func.__name__,
        description=(_inspect.getdoc(func) or "").strip(),
        signature=str(_inspect.signature(func)),
    )


def _get_return_type(func: Callable[..., Any]):
    try:
        sig = inspect.signature(func)
        return (
            sig.return_annotation if sig.return_annotation is not inspect.Signature.empty else None
        )
    except Exception:
        return None


def _augment_prompt(prompt: str, output_type: type | None) -> str:
    """Add minimal, unobtrusive hints to steer models to the expected shape.

    This supplements provider-side structured outputs and helps models that
    ignore response_format by biasing the completion toward strict outputs.
    """
    if output_type is None:
        return prompt
    # Primitive guidance
    if output_type is float:
        guard = (
            "\n\nInstructions: Return only the number as a decimal using '.'; "
            "no currency symbols, units, or extra text."
        )
        return f"{prompt}{guard}"
    if output_type is int:
        guard = "\n\nInstructions: Return only an integer number; no words or punctuation."
        return f"{prompt}{guard}"
    if output_type is bool:
        guard = "\n\nInstructions: Return only true or false in lowercase; no extra text."
        return f"{prompt}{guard}"
    # Dataclass/object guidance: include schema hint for older providers
    try:
        schema = to_json_schema(output_type)
    except Exception:
        schema = None
    if isinstance(schema, dict):
        try:
            schema_json = _json.dumps(schema)
        except Exception:
            schema_json = str(schema)
        guard = (
            "\n\nInstructions: Output only valid JSON matching this schema exactly, "
            "with no commentary, code fences, or extra properties.\n" + schema_json
        )
        return f"{prompt}{guard}"
    return prompt
