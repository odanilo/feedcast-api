from pydantic import BaseModel, Field


class ImportacaoFeedSchema(BaseModel):
    """Define como uma nova importação via rss feed deve ser representado"""

    feed: str

    class Config:
        schema_extra = {
            "example": {"feed": "https://api.jovemnerd.com.br/feed-nerdcast/"}
        }
