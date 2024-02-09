from pydantic import UUID4, BaseModel


class TableBase(BaseModel):
    title: str


class TableCreate(TableBase):
    shop_id: UUID4


class TableUpdate(TableBase):
    pass


class Table(TableBase):
    id: UUID4


class TableItem(Table):
    url: str
