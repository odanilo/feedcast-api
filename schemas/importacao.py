from typing import List
from pydantic import BaseModel, Field

from schemas.episodio import EpisodioViewSchema
from schemas.profile import ProfileViewSchema


class ImportacaoFeedSchema(BaseModel):
    """Define como uma nova importação via rss feed deve ser representada"""

    feed: str

    class Config:
        schema_extra = {
            "example": {"feed": "https://api.jovemnerd.com.br/feed-nerdcast/"}
        }


class ImportacaoFeedViewSchema(BaseModel):
    """Define como será representação do retorno da importação via feed"""

    perfil: ProfileViewSchema
    episodios: List[EpisodioViewSchema]
    erros: List[str]
