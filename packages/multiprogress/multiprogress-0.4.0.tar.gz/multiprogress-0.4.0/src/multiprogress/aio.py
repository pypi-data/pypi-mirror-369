from __future__ import annotations

import asyncio
from asyncio.subprocess import PIPE
from typing import TYPE_CHECKING

import watchfiles
from rich.progress import Progress
from watchfiles import Change

if TYPE_CHECKING:
    from asyncio import Event
    from collections.abc import Callable, Coroutine
    from pathlib import Path
    from typing import Any

    from rich.progress import ProgressColumn


def run(
    args: list[str],
    path: Path | str,
    on_changed: Callable[[set[tuple[Change, str]]], tuple[float, float]],
    *columns: ProgressColumn | str,
    progress: Progress | None = None,
    description: str = "",
    **kwargs,
) -> int:
    coro = arun(
        args,
        path,
        on_changed,
        *columns,
        progress=progress,
        description=description,
        **kwargs,
    )

    return asyncio.run(coro)


async def arun(
    args: list[str],
    path: Path | str,
    on_changed: Callable[[set[tuple[Change, str]]], tuple[float, float]],
    *columns: ProgressColumn | str,
    progress: Progress | None = None,
    description: str = "",
    **kwargs,
) -> int:
    async def coro(update: Callable[[float, float], None]) -> int:
        def _on_changed(changes: set[tuple[Change, str]]) -> None:
            total, completed = on_changed(changes)
            update(total, completed)

        return await execute_watch(args, path, on_changed=_on_changed, **kwargs)

    return await async_progress(
        coro,
        *columns,
        progress=progress,
        description=description,
        **kwargs,
    )


async def execute_watch(
    args: list[str],
    *paths: Path | str,
    on_changed: Callable[[set[tuple[Change, str]]], None],
    **kwargs,
) -> int:
    """Asynchronously execute a command and monitor the output directory.

    This coroutine runs a command with the provided arguments and sets up
    an asynchronous watcher on the specified path. It calls the provided callback
    function with any detected file changes.

    Args:
        args (list[str]): The command-line arguments to run the command.
        paths (Path): Filesystem paths to watch.
        on_changed (Callable[[set[tuple[Change, str]]], None]): A callback function
            that takes a set of changes. Each change is represented by a tuple
            containing the type of change and the path to the changed file.
        **kwargs: Additional keyword arguments to pass to the watchfiles.awatch
            function.

    Returns:
        int: The return code of the process. A return code of 0 indicates
        success, while any non-zero value indicates an error.
    """
    stop_event = asyncio.Event()

    run_task = asyncio.create_task(execute(args, stop_event))
    watch_coro = watch(*paths, stop_event=stop_event, on_changed=on_changed, **kwargs)
    watch_task = asyncio.create_task(watch_coro)

    try:
        await asyncio.gather(run_task, watch_task)

    finally:
        stop_event.set()
        await run_task
        await watch_task

    return run_task.result()


async def execute(args: list[str], stop_event: Event) -> int:
    """Asynchronously execute a subprocess with the given arguments.

    This coroutine starts a subprocess using the provided command-line arguments
    and waits for it to complete. An asyncio.Event is used to signal when the
    subprocess should be stopped.

    Args:
        args (list[str]): The command-line arguments to execute the subprocess.
        stop_event (Event): An event that, when set, signals the coroutine
            to stop waiting and terminate the subprocess if it is still running.

    Returns:
        int: The return code of the subprocess. A return code of 0 indicates success,
        while any non-zero value indicates an error.

    Raises:
        asyncio.CancelledError: If the coroutine is cancelled before the subprocess
        completes its execution.
    """

    try:
        process = await asyncio.create_subprocess_exec(*args, stdout=PIPE, stderr=PIPE)
        return await process.wait()

    finally:
        stop_event.set()


async def watch(
    *paths: Path | str,
    stop_event: Event,
    on_changed: Callable[[set[tuple[Change, str]]], None],
    **kwargs,
) -> None:
    """Asynchronously monitor a directory for file changes and execute a callback.

    This coroutine sets up a watcher on the specified path and listens for file
    changes. When a change is detected, it calls the provided callback function
    with the set of changes. The monitoring continues until the stop_event is set.

    Args:
        paths (Path): Filesystem paths to watch.
        stop_event (Event): An event that, when set, signals the coroutine
            to stop monitoring and terminate.
        callback (Callable[[set[tuple[Change, str]]], None]): A callback function
            that is called with the set of changes detected. Each change is
            represented by a tuple containing the type of change and the path to
            the changed file.
        **kwargs: Additional keyword arguments to pass to the watchfiles.awatch
            function.
    """
    ait = watchfiles.awatch(*paths, stop_event=stop_event, **kwargs)

    async for changes in ait:
        on_changed(changes)


async def async_progress(
    func: Callable[[Callable[[float, float], None]], Coroutine[Any, Any, int]],
    *columns: ProgressColumn | str,
    progress: Progress | None = None,
    description: str = "",
    **kwargs,
) -> int:
    """Execute a function with progress monitoring and display updates.

    Wrap the execution of a provided function (typically a long-running
    process) with a visual progress bar. Update the progress bar based on the
    callback from the wrapped function. The progress bar is displayed in
    the console using the 'rich' library.

    Args:
        func (partial[int]): A partial object that, when called, will execute the
            function with pre-defined arguments. The function is expected to accept
            a callback that updates the progress.
        description (str, optional): A description text to display alongside the
            progress bar. Defaults to an empty string.
        refresh_per_second (float): Number of times per second to refresh the progress
            information. Defaults to 1.

    Returns:
        int: The return code from the executed function. A return code of 0 indicates
        success, while any non-zero value indicates an error.
    """
    if progress is None:
        if not columns:
            columns = Progress.get_default_columns()
        progress = Progress(*columns, **kwargs)
        is_created = True
    else:
        is_created = False

    task_id = progress.add_task(description, total=None)

    last = [0.0]

    def update(total: float, completed: float) -> None:
        last[0] = total
        progress.update(task_id, total=total, completed=completed, refresh=True)

    if is_created:
        progress.start()

    try:
        returncode = await func(update)
        if last[0]:
            progress.update(task_id, total=last[0], completed=last[0], refresh=True)
        return returncode

    finally:
        if is_created:
            progress.stop()
