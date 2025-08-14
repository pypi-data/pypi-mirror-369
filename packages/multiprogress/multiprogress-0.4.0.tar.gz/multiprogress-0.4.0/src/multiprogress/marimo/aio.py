from __future__ import annotations

from typing import TYPE_CHECKING

import marimo._runtime.output._output as output
from marimo._plugins.stateless.status._progress import ProgressBar

from multiprogress.aio import execute_watch

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine
    from pathlib import Path
    from typing import Any

    from watchfiles import Change


async def arun(
    args: list[str],
    path: Path | str,
    on_changed: Callable[[set[tuple[Change, str]]], tuple[int, int]],
    title: str | None = None,
    subtitle: str = "",
    **kwargs,
) -> int:
    async def coro(update: Callable[[int, int], None]) -> int:
        def _on_changed(changes: set[tuple[Change, str]]) -> None:
            total, completed = on_changed(changes)
            update(total, completed)

        return await execute_watch(args, path, on_changed=_on_changed, **kwargs)

    return await async_progress(coro, title, subtitle)


async def async_progress(
    func: Callable[[Callable[[int, int], None]], Coroutine[Any, Any, int]],
    title: str | None = None,
    subtitle: str | None = None,
    completion_title: str | None = None,
    completion_subtitle: str | None = None,
    show_rate: bool = True,
    show_eta: bool = True,
    remove_on_exit: bool = False,
) -> int:
    progress = ProgressBar(
        title,
        subtitle,
        total=None,  # type: ignore
        show_rate=show_rate,
        show_eta=show_eta,
    )
    output.append(progress)

    def update(total: int, completed: int) -> None:
        progress.total = total
        progress.loading_spinner = False
        increment = completed - progress.current
        progress.update(increment)

    try:
        returncode = await func(update)
        progress.update(
            increment=0,
            title=completion_title,
            subtitle=completion_subtitle,
        )
        return returncode

    finally:
        if remove_on_exit:
            progress.clear()
        progress.close()
