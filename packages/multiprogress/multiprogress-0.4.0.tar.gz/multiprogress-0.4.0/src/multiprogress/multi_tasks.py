from __future__ import annotations

from typing import TYPE_CHECKING

from joblib.parallel import Parallel, delayed
from rich.progress import Progress as Super

from .table import create_table

if TYPE_CHECKING:
    from collections.abc import Iterable

    from rich.console import RenderableType


class Progress(Super):
    """A progress bar for multiple tasks."""

    def start_tasks(
        self,
        iterables: Iterable[Iterable[int | tuple[int, int]]],
        parallel: Parallel | None = None,
        n_jobs: int = -1,
    ) -> None:
        """Start multiple tasks.

        Args:
            iterables (Iterable[Iterable[int | tuple[int, int]]]): A collection
                of iterables, each representing a task. Each iterable can yield
                integers (completed) or tuples of integers (total, completed).
            parallel (Parallel | None, optional): A Parallel instance to use.
                Defaults to None.
            n_jobs (int, optional): Number of jobs to run in parallel. Defaults
                to -1, which means using all processors.

        Returns:
            None

        """
        iterables = list(iterables)
        n = len(iterables)

        if self.task_ids:
            task_main = self.task_ids[-1]
        else:
            task_main = None

        task_ids = [
            self.add_task(f"#{i:0>{len(str(n + 1))}}", start=False, total=None)
            for i in range(1, n + 1)
        ]

        def update(i: int) -> None:
            task_id = task_ids[i]

            self.start_task(task_id)

            total = completed = None

            for index in iterables[i]:
                if isinstance(index, tuple):
                    total, completed = index
                else:
                    total, completed = None, index

                self.update(task_id, total=total, completed=completed)

            self.update(task_id, total=total, completed=total, refresh=True)

            if task_main is not None:
                self.update(task_main, advance=1, refresh=True)

            if self.live.transient:
                self.remove_task(task_id)

        parallel = parallel or Parallel(n_jobs=n_jobs, backend="threading")
        parallel(delayed(update)(i) for i in range(n))


class ProgressTable(Progress):
    """A progress bar that displays a table of progress bars."""

    def get_renderables(self) -> Iterable[RenderableType]:
        """Get a number of renderables for the progress display."""
        tasks = [task for task in self.tasks if not task.description.startswith("#")]

        if tasks:
            yield self.make_tasks_table(tasks)

        tasks = [task for task in self.tasks if task.description.startswith("#")]
        tables = [self.make_tasks_table([task]) for task in tasks]

        if tables:
            yield create_table(tables)
