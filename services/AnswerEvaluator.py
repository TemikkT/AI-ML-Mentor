from schemas.evaluation import Evalution
from langchain_core.prompts import PromptTemplate
from schemas.PromptTemplate import EVALUATION_PROMPT


class AnswerEvaluator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def evaluate(self, topic: str, question: str, answer: str) -> Evalution:

        prompt = EVALUATION_PROMPT.format(topic=topic,question=question,answer=answer)
        structured_llm = self.llm.get_structured_llm(Evalution)
        result = structured_llm.invoke(prompt)

        return result