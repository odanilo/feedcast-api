from sqlalchemy import Column, Integer, String, DateTime, func
from typing import Union

from model import Base


class Profile(Base):
    __tablename__ = "profile"

    id = Column("pk_profile", Integer, primary_key=True)
    nome = Column(String(255), unique=True)
    autor = Column(String(140))
    descricao = Column(String(255))
    capa = Column(String(255))
    data_insercao = Column(DateTime, default=func.now())

    def __init__(
        self,
        nome: str,
        autor: str,
        descricao: str,
        capa: str,
        data_insercao: Union[DateTime, None] = None,
    ):
        """
        Cria um Profile

        Arguments:
            nome: nome do podcast
            autor: nome do autor do podcast
            descrição: descrição do podcast
            capa: capa do episódio
            data_insercao: data de quando o produto foi inserido à base
        """
        self.nome = nome
        self.autor = autor
        self.descricao = descricao
        self.capa = capa

        # se não for informada, será o data exata da inserção no banco
        if data_insercao:
            self.data_insercao = data_insercao
