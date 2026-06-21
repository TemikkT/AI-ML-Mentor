from schemas.evaluation import Evalution
from schemas.training_result import ExecutionResult
from config.prompts import PRACTICE_EVALUATION_PROMPT

"""
Аналог AnswerEvaluator для тренажёра.

Отличие от AnswerEvaluator: помимо топика, вопроса и ответа (кода) пользователя,
сюда дополнительно подаётся результат выполнения этого кода (ExecutionResult)
или None, если код не выполнялся (например, тема SQL на этой итерации —
она оценивается как текст, как и в AnswerEvaluator).

Используем тот же llm_client и ту же схему Evalution — оценка по структуре
не отличается от теоретического режима, отличается только промпт.
"""


class PracticeEvaluator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def evaluate(self, topic: str, question: str, answer: str,
                  execution_result: ExecutionResult | None = None) -> Evalution:

        execution_text = self._format_execution_result(execution_result)

        prompt = PRACTICE_EVALUATION_PROMPT.format(
            topic=topic,
            question=question,
            answer=answer,
            execution_result=execution_text,
        )

        structured_llm = self.llm.get_structured_llm(Evalution)
        result = structured_llm.invoke(prompt)

        print(result)
        print(type(result))

        return result

    def _format_execution_result(self, execution_result: ExecutionResult | None) -> str:
        """
        Превращает ExecutionResult в текстовый блок для промпта.
        Если execution_result is None (код не выполнялся, например тема SQL),
        явно сообщаем об этом модели, чтобы она оценивала как текст.
        """
        if execution_result is None:
            return "Код не выполнялся (эта тема оценивается без выполнения)."

        if execution_result.timed_out:
            return (
                "Код не успел выполниться за отведённое время (timeout). "
                f"Частичный stdout: {execution_result.stdout!r}"
            )

        if execution_result.success:
            return f"Код выполнился успешно.\nstdout:\n{execution_result.stdout}"

        return (
            f"Код выполнился с ошибкой.\n"
            f"stdout:\n{execution_result.stdout}\n"
            f"stderr:\n{execution_result.stderr}"
        )
