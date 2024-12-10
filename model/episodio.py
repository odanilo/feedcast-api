from sqlalchemy import Column, String, Integer, DateTime, func
from typing import Union

from model import Base


class Episodio(Base):
    __tablename__ = "episodio"

    id = Column("pk_episodio", Integer, primary_key=True)
    titulo = Column(String(255), unique=True)
    audio = Column(String(500))
    capa = Column(String(500))
    descricao = Column(String(500))
    data_insercao = Column(DateTime, default=func.now())

    def __init__(
        self,
        titulo: str,
        audio: str,
        capa: str,
        descricao: str,
        data_insercao: Union[DateTime, None] = None,
    ):
        """
        Cria um Episódio

        Arguments:
            titulo: título do episódio
            audio: link para o arquivo de áudio daquele episódio
            capa: link para o arquivo da capa daquele episódio
            descrição: descrição do episódio
            data_insercao: data de quando o produto foi inserido à base
        """
        self.audio = audio
        self.capa = capa
        self.descricao = descricao
        self.titulo = titulo

        # se não for informada, será o data exata da inserção no banco
        if data_insercao:
            self.data_insercao = data_insercao
