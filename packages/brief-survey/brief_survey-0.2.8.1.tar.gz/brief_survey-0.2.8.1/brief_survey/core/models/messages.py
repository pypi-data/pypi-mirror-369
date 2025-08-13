from pydantic import BaseModel, Field


class InfoMessages(BaseModel):
    invalid_input:str = Field(default="Пожалуйста, введите корректные данные.",)
    save_success:str = Field(default="Спасибо! Данные успешно сохранены.",)
    save_fail:str = Field(default="Произошла ошибка при сохранении. Попробуйте позже.",)
    finish_text:str = Field(default="Данные приняты.",)
    question_not_found:str = Field(default= "Ошибка: вопрос не найден.")
    pre_save_message:str = Field(default= "Сохраняю")
    start_message:str = Field(default=None)
    forced_exit_message:str = Field(default="Выход из опроса.Введенные данные не позволяют продолжить опрос")
    no_confirmed_data:str = Field(default='Укажите запрашиваемые данные чтобы продолжить...')

    class Config:
        from_attributes=True
