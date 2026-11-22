"""Execução de tarefas bloqueantes (PackageKit, Flatpak, análise de hardware) fora da
thread da interface, sem depender de Qt Widgets."""

import traceback

from PyQt6.QtCore import QThread, pyqtSignal

from .i18n import _


class Worker(QThread):
    """Executa `func(*args, progress=cb)` numa thread e emite o resultado."""

    progressed = pyqtSignal(object, object)   # percent | None, status | None
    succeeded = pyqtSignal(object)
    failed = pyqtSignal(str, str)              # mensagem amigável, detalhes técnicos

    def __init__(self, func, *args, parent=None, with_progress=True, **kwargs):
        super().__init__(parent)
        self._func, self._args, self._kwargs = func, args, kwargs
        self._with_progress = with_progress

    def run(self):
        try:
            if self._with_progress:
                self._kwargs["progress"] = lambda pct, status: self.progressed.emit(pct, status)
            self.succeeded.emit(self._func(*self._args, **self._kwargs))
        except Exception as exc:  # noqa: BLE001 — tudo vira mensagem compreensível
            details = getattr(exc, "details", "") or traceback.format_exc()
            self.failed.emit(str(exc) or _("Something went wrong"), details)


class WorkerPool:
    """Mantém referências aos workers ativos (evita coleta pelo GC no meio da tarefa)."""

    def __init__(self):
        self._items = []

    def start(self, worker, ok=None, fail=None, progress=None):
        self._items.append(worker)
        if ok:
            worker.succeeded.connect(ok)
        if fail:
            worker.failed.connect(fail)
        if progress:
            worker.progressed.connect(progress)
        worker.finished.connect(lambda: self._items.remove(worker) if worker in self._items else None)
        worker.start()
        return worker
