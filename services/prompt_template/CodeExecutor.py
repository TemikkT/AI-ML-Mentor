import subprocess
import sys

from schemas.training_result import ExecutionResult

"""
Класс для безопасного выполнения кода пользователя (Python/Pandas).

Логика простая и без лишней инфраструктуры:
- код запускается в ОТДЕЛЬНОМ процессе (subprocess), а не через exec()
  в текущем процессе — чтобы зависший или упавший код пользователя
  не мог повлиять на работу основного приложения.
- ограничение по времени (timeout) — если код не успел выполниться,
  процесс принудительно завершается.
- результатом является stdout (всё, что пользователь вывел через print()),
  и именно через print() задача просит предоставить итоговый результат.

Для SQL-тем (которые оцениваются как текст на этой итерации)
CodeExecutor вообще не вызывается — это решает PracticeTrainer,
видя тему вопроса (см. config.practice_config.EXECUTABLE_TOPICS).
"""


class CodeExecutor:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def run(self, code: str) -> ExecutionResult:
        """
        Выполняет переданный Python-код в отдельном процессе
        и возвращает результат (stdout/stderr/успех/таймаут).
        """
        try:
            process = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            return ExecutionResult(
                stdout=process.stdout,
                stderr=process.stderr,
                success=(process.returncode == 0),
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            # Код не успел выполниться за отведённое время —
            # частично собранный stdout/stderr всё равно может быть полезен LLM.
            stdout = e.stdout if isinstance(e.stdout, str) else (e.stdout or b"").decode(errors="replace")
            stderr = e.stderr if isinstance(e.stderr, str) else (e.stderr or b"").decode(errors="replace")

            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                success=False,
                timed_out=True,
            )
