

from typing import List
from pydantic import UUID4, BaseModel


class MessageWidget(BaseModel):
    widget_type: str
    id: UUID4
    message: str


class Choice(BaseModel):
    id: UUID4
    text: str


class MenuWidget(BaseModel):
    widget_type: str
    id: UUID4
    choices: List[Choice]


class SliderWidgetSlide(BaseModel):
    id: UUID4
    title: str = None
    image: str = None
    choices: List[Choice]


class SliderWidget(BaseModel):
    widget_type: str
    id: UUID4
    slides: List[SliderWidgetSlide]


slides = {
    "widget_type": "SLIDER",
    "id": "37142f49-d49c-4e76-b1a4-e678494ba349",
    "slides": [
        {
            "image": "",
            "title": "title1",
            "subtitle": "subtitle1",
            "choices": [
                {"id": "d9344eff-b417-4721-8984-bb8fbffb21d1", "text": "Choice1"},
                {"id": "2e259e5b-2c3f-4da6-a7d6-fd95dec40ba2", "text": "Choice2"},
                {"id": "aa124532-2290-44c7-b0f5-3ec8cf8f4c83", "text": "Choice3"}
            ]
        }, {
            "image": "",
            "title": "title2",
            "subtitle": "subtitle2",
            "choices": [
                {"id": "d9344eff-b417-4721-8984-bb8fbffb21d4", "text": "Choice1"},
                {"id": "2e259e5b-2c3f-4da6-a7d6-fd95dec40ba7", "text": "Choice2"},
                {"id": "aa124532-2290-44c7-b0f5-3ec8cf8f4c88", "text": "Choice3"}
            ]
        }
    ]
}
