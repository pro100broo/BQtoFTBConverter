from pydantic import BaseModel


class LoggerData(BaseModel):
    uid: str
    name: str


class CheckBoxTask(BaseModel):
    uid: str
    type: str


class LocationTask(BaseModel):
    uid: str
    type: str
    dimension: int
    dimension_name: str
    x: int
    y: int
    z: int


class HuntTask(BaseModel):
    uid: str
    type: str
    entity: str
    count: int


class StandardTask(BaseModel):
    uid: str
    type: str
    icon: str | None
    item: str | None
    count: int | None
    consume_items: bool | None
    ignore_nbt: bool | None


class ItemQuest(BaseModel):
    uid: str
    id: int
    name: str | None
    icon: str | None
    text: str | None
    x: float | None
    y: float | None
    dependencies: list[int] | list | None
    hide_dependency_lines: bool | None
    tasks: list[StandardTask | CheckBoxTask | HuntTask | LocationTask] | None


class Tab(BaseModel):
    uid: str
    name: str
    description: str | None
    quests: list[ItemQuest] | None


class Tabs(BaseModel):
    tabs: list[Tab]
