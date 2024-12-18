from datetime import datetime

from typing import Optional
from pydantic import BaseModel

from model.profile import Profile


class ProfileSchema(BaseModel):
    """Define como um novo Profile a ser inserido deve ser representado"""

    nome: str
    autor: str
    descricao: str
    capa: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "nome": "NerdCast",
                "autor": "Jovem Nerd",
                "descricao": "O mundo vira piada no Jovem Nerd",
                "capa": "https://jovemnerd.com.br/wp-content/themes/jovem-nerd-v9/assets/images/nc-feed.jpg",
            }
        }


class ProfileViewSchema(BaseModel):
    """Define como um Profile será retornado"""

    id: int = 1
    nome: str = "NerdCast"
    autor: str = "Jovem Nerd"
    descricao: str = "O mundo vira piada no Jovem Nerd"
    capa: Optional[str] = (
        "https://jovemnerd.com.br/wp-content/themes/jovem-nerd-v9/assets/images/nc-feed.jpg"
    )
    data_insercao: Optional[datetime] = None


class ProfileDelSchema(BaseModel):
    """Define como deve ser a estrutura do dado retornado após uma requisição
    de remoção.
    """

    mesage: str
    titulo: str


def apresenta_profile(profile: Profile):
    """Retorna uma representação do Profile seguindo o schema definido em ProfileSchema."""
    return {
        "id": profile.id,
        "nome": profile.nome,
        "autor": profile.autor,
        "descricao": profile.descricao,
        "capa": profile.capa,
        "data_insercao": profile.data_insercao.isoformat() + "Z",
    }
