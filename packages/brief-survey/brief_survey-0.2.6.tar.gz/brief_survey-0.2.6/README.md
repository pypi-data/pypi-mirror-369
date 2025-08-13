# Оглавление

## 🇺🇸 English

- [BriefSurvey Universal Dynamic Survey for Telegram Bots](#briefsurvey-universal-dynamic-survey-for-telegram-bots-with-aiogram-version-3-aiogram_dialog-and-pydantic)
- [Description](#description)
- [Installation](#installation)
  - [From GitHub Repository](#from-github-repository)
  - [Download Locally and Install](#download-locally-and-install)
- [Quick Start](#quick-start)
  - [(case 1) Dynamic create a brief](#case-1-dynamic-crate-a-brief)
  - [(case 2)](#case-2)
    - [1. Define your questions using Pydantic models](#1-define-your-questions-using-pydantic-models)
    - [2. Define a result model](#2-define-a-result-model)
    - [3. Create a function to save results](#3-create-a-function-to-save-results)
    - [4. Initialize and register the survey](#4-initialize-and-register-the-survey)
    - [5. Launch the survey in Telegram with the command](#5-launch-the-survey-in-telegram-with-the-command)
- [Important](#important)
- [Customizing Messages and Buttons in brief_survey](#customizing-messages-and-buttons-in-brief_survey)
  - [What can be customized (English)](#what-can-be-customized-english)
    - [InfoMessages — system messages](#infomessages-—-system-messages)
    - [InfoButtons — button labels](#infobuttons-—-button-labels)
  - [Example usage](#example-usage)

## 🇷🇺 Русский

- [BriefSurvey](#briefsurvey)
- [Описание](#описание)
- [Установка](#установка)
  - [Github Repo](#github-repo)
  - [Скачать локально и установить](#скачать-локально-и-установить)
- [Быстрый старт](#быстрый-старт)
  - [(1 вариант) Динамическое добавление вопросов](#1-вариант-динамическое-добавление-вопросов)
  - [(2 вариант)](#2-вариант)
    - [1. Определите вопросы](#1-определите-вопросы)
    - [2. Определите модель результата](#2-определите-модель-результата)
    - [3. Создайте функцию для сохранения результатов](#3-создайте-функцию-для-сохранения-результатов)
    - [4. Инициализируйте и зарегистрируйте опросник](#4-инициализируйте-и-зарегистрируйте-опросник)
    - [5. Запускайте команду в Telegram](#5запускайте-команду-в-telegram)
- [Важно](#важно)
- [Настройка сообщений и кнопок в brief_survey](#настройка-сообщений-и-кнопок-в-brief_survey)
  - [Что можно настраивать](#что-можно-настраивать)
    - [InfoMessages — системные сообщения](#infomessages-—-системные-сообщения)
    - [InfoButtons — тексты кнопок](#infobuttons-—-тексты-кнопок)
  - [Пример использования](#пример-использования)

# 🇺🇸 English

## BriefSurvey
Universal Dynamic Survey for Telegram Bots with `aiogram` version 3 `aiogram_dialog` and Pydantic
### Description
BriefSurvey is a module for quick and flexible creation of dialog-based surveys in Telegram using aiogram v3 and aiogram_dialog.

- Questions are defined using Pydantic models to enforce strong typing and validation.
- Final answers are automatically serialized back into a Pydantic result model.
- Easy to extend and customize.
- Supports different question types: text, number, single-choice, multiple-choice.
- Simple integration and handler registration.
- Auto-validation questions by names.Questions with names like "age", "weight" validate and send error messages automatically without validator enter.


---
## Installation
### From GitHub Repository

```bash
pip install git+https://github.com/Fugguri/brief_survey.git 
```
### Download Locally and Install

```bash
git clone https://github.com/Fugguri/brief_survey.git
pip install -e brief_survey 
```


## Quick Start
### (case 1) Dynamic crate a brief 
```python
from brief_survey import BriefSurvey
from brief_survey.validators.person import age
async def save_handler(user_id: int, result: any):
    # dynamic access to survey result fields by question name.
    name = result.name
    age = result.age
    gender = result.gender

    return

survey = BriefSurvey(
    save_handler=save_handler,
    start_command='start_brief'  # customizable start command for the survey
)

# Customizable error messages
survey.info_messages.invalid_input = "Invalid data received, please try again."
# Customizable button text at the end of the survey
survey.buttons.finish_text = "Finish survey"

survey.add_question(
    text="What is your name?",
    question_type="text",
    name="name",
    media_path='storage/media/img.png'  # you can send media with text for any question (optional)
)

survey.add_question(
    text="Your age?",
    question_type="number",
    name="age",
    validator=age # You can use validators from validators path of this lib.
)


survey.add_question(
    text="Select your gender",
    question_type="choice",
    name="gender",
    choices=["Male", "Female"],
    next_questions={
        'Male': "favorite_car",
        'Female': "favorite_color",
    }
)

survey.add_question(
    text="Favorite car brand?",
    question_type="choice",
    name="favorite_car",
    choices=["MBW", "Mercedes"],
    next_question='photo'  # mandatory parameter for queries depending on choice. If not set, proceeds to next survey question
)

survey.add_question(
    text="Favorite color?",
    question_type="choice",
    name="favorite_color",
    choices=["White", "Pink", "Black"],
    next_question='photo'  # mandatory parameter for queries depending on choice. If not set, proceeds to next survey question
)

survey.add_question(
    text="Upload your photo",
    question_type="photo",
    name="photo"
)

```
### (case 2) 1. Define your questions using Pydantic models:

```python
from brief_survey import QuestionBase, ChoiceQuestion, MultiChoiceQuestion

questions = [
    QuestionBase(
        name="name",
        text="What is your name?",
        type="text",
        validator=lambda x: bool(x.strip()),
    ),
    ChoiceQuestion(
        name="gender",
        text="Select your gender",
        type="choice",
        choices=[("1", "Male"), ("2", "Female")],
    ),
    MultiChoiceQuestion(
        name="profession",
        text="Select your profession",
        type="multi_choice",
        choices=[
            ("1", "Athlete"),
            ("2", "Entrepreneur"),
            ("3", "Worker"),
        ],
    ),
]

```
### 2. Define a result model:
``` python
from pydantic import BaseModel
from typing import Optional

class SurveyResult(BaseModel):
    name: Optional[str]
    gender: Optional[str]
    profession: Optional[list[str]]
```
### 3. Create a function to save results:
``` python
async def save_handler(user_id: int, result: SurveyResult):
    # Save logic, e.g., store in database
    print(f"User {user_id} survey result: {result}")

```
### 4. Initialize and register the survey:
``` python
from brief_survey import BriefSurvey

survey = BriefSurvey(
    questions=questions,
    save_handler=save_handler,
    result_model=SurveyResult,
)

# In your main bot file with Dispatcher dp
survey.register_handlers(
    dp=dp,
    command_start='start_survey',     # optional
    text='Start survey',               # optional
    callback_data="start_survey"       # optional
)
```
### 5. Launch the survey in Telegram with the command:
 /start_survey



## Important
If you have global handlers in your bot, filter states explicitly using StateFilter to avoid conflicts that can break the survey after the first message:
``` python
from aiogram.filters import StateFilter

dp.message.register(handle, StateFilter(None))          # Only outside states
dp.callback_query.register(handle_callback, StateFilter(None))
```
# Customizing Messages and Buttons in brief_survey

The **brief_survey** library provides `InfoMessages` and `InfoButtons` classes that allow you to easily customize system messages and button texts used in the survey dialogs.

## What can be customized (English)

### InfoMessages — system messages

| Field                   | Description                                       | Default example                  |
|-------------------------|-------------------------------------------------|---------------------------------|
| `invalid_input`          | Message shown when user input is invalid         | `"Please enter valid data."`    |
| `save_success`           | Message confirming data saved successfully       | `"Thank you! Data saved successfully."` |
| `save_fail`              | Message shown if saving data failed               | `"An error occurred during saving. Please try again later."` |
| `finish_text`            | Text displayed at survey completion               | `"Data received."`              |
| `question_not_found`     | Message shown if question is not found            | `"Error: question not found."`  |
| `pre_save_message`       | Message shown before saving data                   | `"Saving..."`                   |
| `start_message`          | Message shown at start of survey (optional)       | `None`                         |
| `forced_exit_message`    | Message shown when survey is forcefully exited    | `"Survey exited. Entered data does not allow continuation."` |

### InfoButtons — button labels

| Field                  | Description                                      | Default example                 |
|------------------------|-------------------------------------------------|--------------------------------|
| `finish_text`           | Text on the button to finish the survey          | `"Finish"`                    |
| `multi_select_confirm`  | Text for confirming multi-select choice          | `"Confirm selection"`          |
| `start_again`           | Text on the button to restart the survey         | `"Start again"`                |

## Example usage
``` python 
Setting system messages
survey.info_messages.invalid_input = "Invalid data received, please try again."
survey.info_messages.save_success = "Thank you! Your responses have been saved."
survey.info_messages.save_fail = "Saving failed, please try again later."
survey.info_messages.finish_text = "Thank you for participating!"
survey.info_messages.question_not_found = "Question not found."
survey.info_messages.pre_save_message = "Saving data..."
survey.info_messages.start_message = "Let's start the survey!"
survey.info_messages.forced_exit_message = "Survey terminated due to an error."

Setting button texts
survey.buttons.finish_text = "Finish survey"
survey.buttons.multi_select_confirm = "Confirm"
survey.buttons.start_again = "Restart"
```



# 🇷🇺 Русский

## BriefSurvey

Универсальный динамический опросник для Telegram-ботов на базе `aiogram_dialog` с поддержкой Pydantic-моделей вопросов и результатов.

---

## Описание

BriefSurvey — это модуль для быстрой и гибкой реализации диалоговых опросников в Telegram с помощью `aiogram` 3-й версии и `aiogram_dialog`.

- Вопросы описываются Pydantic-моделями для строгой типизации и валидации.
- Итоговые ответы автоматически сериализуются обратно в Pydantic-модель результата.
- Легко расширяется и настраивается.
- Позволяет реализовать опросник с разными типами вопросов: текст, число, выбор одного или нескольких вариантов.
- Простое подключение и регистрация обработчиков.
- Автоматическая валидация по имени вопроса. Поля типа "age", "weight" проходят автоматическую валидацию и присылают сообщение об ошибке, без указания валидаторов .

---

## Установка
### Github Repo
```bash
pip install git+https://github.com/Fugguri/brief_survey.git 
```
### Скачать локально и установить
```bash
git clone https://github.com/Fugguri/brief_survey.git
pip install -e brief_survey 
```


## Быстрый старт
### (1 вариант) Динамическое добавление вопросов
```python

from brief_survey import BriefSurvey
async def save_handler(user_id: int, result: any):
    #динамическое обращение к полям результата опроса по имени вопроса. 
    name = result.mame
    age = result.age
    gender = result.gender 
    return 
survey = BriefSurvey(
    save_handler=save_handler,
    start_command='start_brief' # Можно настраивать команду начала опроса
)

#Можно настраивать сообщения об ошибках
survey.info_messages.invalid_input = "Получены неверные данные, попробуйте еще раз"

#Можно настраивать сообщени и кнопку в конце опроса
survey.info_messages.invalid_input = "Получены неверные данные, попробуйте еще раз"
survey.buttons.finish_text = "Завершить опрос" 
# Если необходимо можете отправить сообщение перед началом опроса
survey.info_messages.start_message = 'Пройдите небольшой опрос перед началом работы с ботом.'
from brief_survey.validators.person import age  
survey.add_question(
    text="Как вас зовут?",
    question_type="text",
    name="name",
    media_path='storage/media/img.png'# Можете отправлять фотографии вместе с вопросом
)
survey.add_question(
    text="Ваш возраст?",
    question_type="number",
    name="age",
    validator=age # Вы можете использовать готовые валидаторы из раздела validators
)
survey.add_question(
    text="Выберите пол",
    question_type="choice",
    name="gender",
    choices=["Мужской", "Женский"],
    
    next_questions={
    'Мужской': "favorite_car",
    'Женский': "favorite_color",
    }
    
)
survey.add_question(
    text="Любимая марка автомобиля?",
    question_type="choice",
    name="favorite_car",
    choices=["MBW", "Mercedes"],
    next_question='photo' # Обязательный параметр для вариантов зависящих от выбора. Если не указать, пойдет дальше по опросу

)
survey.add_question(
    text="Любимый цвет?",
    question_type="choice",
    name="favorite_car",
    choices=["Белый", "Розовый", "Черный"],
    next_question='photo' # Обязательный параметр для вариантов зависящих от выбора. Если не указать, пойдет дальше по опросу
)

survey.add_question(
    text="Загрузите ваше фото",
    question_type="photo",
    name="photo"
)

````

### (2 вариант) 
1. Определите вопросы (используйте модели из основного модуля):

```python
from brief_survey import QuestionBase, ChoiceQuestion, MultiChoiceQuestion

questions = [
    QuestionBase(
        name="name",
        text="Как вас зовут?",
        type="text",
        validator=lambda x: bool(x.strip()),
    ),
    ChoiceQuestion(
        name="gender",
        text="Выберите пол",
        type="choice",
        choices=[("1", "Мужской"), ("2", "Женский")],
    ),
    MultiChoiceQuestion(
        name="gender",
        text="Выберите род деятельности",
        type="multi_choice",
        choices=[("1", "Спортсмен"), 
                 ("2", "Предприниматель"),
                 ("3", "Простой работник")
                 ],
    )
]



```
### 2. Определите модель результата:
``` python
from pydantic import BaseModel
from typing import Optional


class SurveyResult(BaseModel):
    name: Optional[str]
    gender: Optional[str]
```
### 3. Создайте функцию для сохранения результатов:
```python

async def save_handler(user_id: int, result: SurveyResult):
    # Логика сохранения, например, в базу
    print(f"Результат опроса пользователя {user_id}: {result}")
```
### 4. Инициализируйте и зарегистрируйте опросник:
``` python
from brief_survey import BriefSurvey

survey = BriefSurvey(
    questions=questions,
    save_handler=save_handler,
    result_model=SurveyResult,
)

# в основном файле с ботом (Dispatcher dp) регистрация в Dispatcher
survey.register_handlers(dp=dp,
                         command_start='start_survey', #опционально
                         text='Начать опрос', #опционально
                         callback_data="start_survey" #опционально
                         )
```
### 5.Запускайте команду в Telegram:

/start_survey

## Важно

Если у вас есть глобальный handler, фильтруйте state вручную, при помощи StateFilter.
Неясные конфликты и после первого сообщения опросник перестает работать.

``` python
from aiogram.filters import StateFilter
dp.message.register(handle,StateFilter(None))  # только вне состояний!
dp.callback_query.register(handle_callback,StateFilter(None))
```
## Настройка сообщений и кнопок в brief_survey

В библиотеке **brief_survey** доступны классы `InfoMessages` и `InfoButtons`, которые позволяют легко настраивать тексты системных сообщений и кнопок, используемых в диалогах опросника.

### Что можно настраивать

#### InfoMessages — системные сообщения

| Поле                    | Описание                                             | Пример по умолчанию                                  |
|-------------------------|-----------------------------------------------------|-----------------------------------------------------|
| `invalid_input`          | Сообщение при неверном вводе                         | `"Пожалуйста, введите корректные данные."`          |
| `save_success`           | Сообщение об успешном сохранении                     | `"Спасибо! Данные успешно сохранены."`              |
| `save_fail`              | Сообщение об ошибке при сохранении                   | `"Произошла ошибка при сохранении. Попробуйте позже."` |
| `finish_text`            | Текст при завершении опроса                          | `"Данные приняты."`                                  |
| `question_not_found`     | Сообщение при ошибке отсутствия вопроса              | `"Ошибка: вопрос не найден."`                        |
| `pre_save_message`       | Сообщение перед отправкой данных на сохранение       | `"Сохраняю"`                                         |
| `start_message`          | Сообщение при начале опроса (опционально)            | `None`                                              |
| `forced_exit_message`    | Сообщение при принудительном выходе из опроса        | `"Выход из опроса.Введенные данные не позволяют продолжить опрос"` |

#### InfoButtons — тексты кнопок

| Поле                   | Описание                                          | Пример по умолчанию               |
|------------------------|---------------------------------------------------|----------------------------------|
| `finish_text`           | Надпись на кнопке завершения опроса                | `"Завершить"`                    |
| `multi_select_confirm`  | Текст кнопки для подтверждения выбора (множественный выбор) | `"Подтвердить выбор"`            |
| `start_again`           | Текст кнопки для перезапуска опроса                 | `"Начать сначала"`               |

### Пример использования
``` python Настройка сообщений об ошибках и событий
survey.info_messages.invalid_input = "Получены неверные данные, попробуйте еще раз"
survey.info_messages.save_success = "Спасибо! Ваши ответы сохранены."
survey.info_messages.save_fail = "Ошибка при сохранении, попробуйте позже."
survey.info_messages.finish_text = "Спасибо за участие!"
survey.info_messages.question_not_found = "Вопрос не найден."
survey.info_messages.pre_save_message = "Данные сохраняются..."
survey.info_messages.start_message = "Начинаем опрос!"
survey.info_messages.forced_exit_message = "Опрос прерван из-за ошибки."

Настройка текстов кнопок
survey.buttons.finish_text = "Завершить опрос"
survey.buttons.multi_select_confirm = "Подтвердить"
survey.buttons.start_again = "Начать заново"
```



# ToDo
- add media list handler
- check same questions name in list
- add survey database saver. To save complete survey_to database. And call by his id
# for any errors send me a telegram message to [@fugguri](https://t/me/fugguri).
# ☕️bye me a coffe appreciated 