from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from model.episodio import Episodio


class EpisodioSchema(BaseModel):
    """Define como um novo Episodio a ser inserido deve ser representado"""

    titulo: str
    descricao: str
    capa: Optional[str]
    audio: str

    class Config:
        schema_extra = {
            "example": {
                "titulo": "NerdCast 961 - Qual é a pauta?",
                "descricao": "Projeto Velho Gostoso, nostalgia e o que seu algoritmo diz sobre você",
                "capa": "https://example.com/image.jpg",
                "audio": "https://example.com/audio.mp3",
            }
        }


class EpisodioDelSchema(BaseModel):
    """Define como deve ser a estrutura do dado retornado após uma requisição
    de remoção de um Episodio.
    """

    mesage: str
    titulo: str


class EpisodioViewSchema(BaseModel):
    """Define como um Episodio será retornado"""

    id: int = 1
    titulo: str = "NerdCast 961 - Qual é a pauta? O que você procura está aqui!"
    descricao: str = (
        "Projeto Velho Gostoso, nostalgia e o que seu algoritmo diz sobre você"
    )
    capa: Optional[str] = (
        "https://uploads.jovemnerd.com.br/wp-content/uploads/2024/12/nc961_sem_pauta_24_3000x3000px__56k6wcp0.jpg"
    )
    audio: str = (
        "https://chrt.fm/track/GD6D57/https://nerdcast.jovemnerd.com.br/nerdcast_961_sempauta.mp3"
    )
    data_insercao: Optional[datetime] = None


class EpisodioPath(BaseModel):
    """Define o parâmetro das rotas de Episodio que exigem um ID"""

    episodio_id: int = Field(..., description="Episódio ID")


def apresenta_episodio(episodio: Episodio):
    """Retorna uma representação do Episodio seguindo o schema definido em EpisodioSchema."""
    return {
        "id": episodio.id,
        "titulo": episodio.titulo,
        "descricao": episodio.descricao,
        "capa": episodio.capa,
        "audio": episodio.audio,
        "data_insercao": episodio.data_insercao.isoformat() + "Z",
    }


def apresenta_episodios(episodios: List[Episodio]):
    """Retorna uma representação do Episodio seguindo o schema definido em
    EpisodioViewSchema.
    """
    result = []
    for episodio in episodios:
        result.append(
            {
                "id": episodio.id,
                "titulo": episodio.titulo,
                "descricao": episodio.descricao,
                "capa": episodio.capa,
                "audio": episodio.audio,
                "data_insercao": episodio.data_insercao.isoformat() + "Z",
            }
        )

    return {"episodios": result}
