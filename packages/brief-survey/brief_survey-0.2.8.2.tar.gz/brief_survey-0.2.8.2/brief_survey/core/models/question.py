from typing import List, Optional, Tuple, Callable, Union, Literal, Dict
from pydantic import BaseModel, field_validator

from brief_survey.core.exceptions.questions import UnknownQuestionTypeError

QuestionType = Literal["text", "number",'with_confirm', "choice", "multi_choice", "photo", "video", "media"]


class QuestionBase(BaseModel):
    name: str
    text: str
    type: QuestionType
    validator: Optional[Callable[[str], bool]] = None
    next_questions: Optional[Dict[str, str]] = None  # например {"Yes": "q3", "No": "q4"}
    next_question: Optional[str] = None,  # name следующего вопроса, нужно для ветвления запросов
    media: Optional[str] = None,
    forced_exit_validator: Optional[Callable[[str], bool]] = None
    validator_error_message: Optional[str] =None
    confirm_field_name:Optional[str] ="Введенные данные:"
    @field_validator('type')
    def type_must_be_known(cls, v):
        if v not in QuestionType.__args__:  # type: ignore
            raise UnknownQuestionTypeError
        return v


class ChoiceQuestion(QuestionBase):
    choices: List[Tuple[str | int, str]]

    @field_validator("choices")
    def check_choices_non_empty(cls, v, values):
        if not v or not isinstance(v, list):
            raise ValueError("Choices must be a non-empty list")
        return v


class MultiChoiceQuestion(QuestionBase):
    choices: List[Tuple[str, str]]

    @field_validator("choices")
    def check_choices_non_empty(cls, v, values):
        if not v or not isinstance(v, list):
            raise ValueError("Choices must be a non-empty list")
        return v


Question = Union[QuestionBase, ChoiceQuestion, MultiChoiceQuestion]


# Пример модели результата, пользователь сам может создать свою
class SurveyResult(BaseModel):
    name: Optional[str]
    age: Optional[int]
    gender: Optional[str]


QUESTION_TYPE_MAP = {
    "text": QuestionBase,
    "with_confirm": QuestionBase,
    "photo": QuestionBase,
    "video": QuestionBase,
    "media": QuestionBase,
    "number": QuestionBase,
    "choice": ChoiceQuestion,
    "multi_choice": MultiChoiceQuestion,
}