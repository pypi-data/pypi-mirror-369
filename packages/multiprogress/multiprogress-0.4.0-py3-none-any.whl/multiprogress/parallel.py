"""Provide a progress bar for parallel task execution."""

from __future__ import annotations

from typing import TYPE_CHECKING

from joblib.parallel import Parallel
from rich.progress import Progress as Super

if TYPE_CHECKING:
    from collections.abc import Callable


# https://github.com/jonghwanhyeon/joblib-progress/blob/main/joblib_progress/__init__.py
class Progress(Super):
    _print_progress: Callable[[Parallel], None] | None = None

    def start(self) -> None:
        super().start()

        self._print_progress = Parallel.print_progress

        def _update(parallel: Parallel) -> None:
            update(self, parallel)

        Parallel.print_progress = _update  # type: ignore

    def stop(self) -> None:
        if self._print_progress:
            Parallel.print_progress = self._print_progress  # type: ignore

        super().stop()


def update(progress: Progress, parallel: Parallel) -> None:
    if progress.task_ids:
        task_id = progress.task_ids[-1]
    else:
        task_id = progress.add_task("", total=None)

    progress.update(task_id, completed=parallel.n_completed_tasks, refresh=True)

    if progress._print_progress:
        progress._print_progress(parallel)
