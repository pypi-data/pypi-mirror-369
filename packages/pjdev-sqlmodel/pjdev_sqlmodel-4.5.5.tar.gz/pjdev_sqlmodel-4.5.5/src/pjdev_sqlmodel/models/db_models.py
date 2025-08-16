from typing import Optional

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field as SqlField


class ModelBase(SQLModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class TableModel(ModelBase):
    row_id: Optional[int] = SqlField(default=None, primary_key=True)
