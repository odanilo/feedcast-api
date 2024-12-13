import feedparser

from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from flask_cors import CORS

from sqlalchemy.exc import IntegrityError, NoResultFound

from model import Session, Episodio, Profile
from logger import logger

from schemas.episodio import (
    EpisodioDelSchema,
    EpisodioSchema,
    EpisodioPath,
    EpisodioViewSchema,
    apresenta_episodio,
    apresenta_episodios,
)
from schemas.error import ErrorSchema
from schemas.profile import ProfileSchema, apresenta_profile, ProfileDelSchema

info = Info(title="Poscast API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(
    name="Documentação",
    description="Seleção de documentação: Swagger, Redoc ou RapiDoc",
)
episodio_tag = Tag(
    name="Episódio",
    description="Adição, visualização e remoção de episódios de podcast à base",
)
profile_tag = Tag(
    name="Profile",
    description="Adição, visualização e deleção do profile do podcast",
)


@app.get("/", tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação."""
    return redirect("/openapi")


@app.post(
    "/episodios",
    tags=[episodio_tag],
    responses={"200": EpisodioSchema, "409": ErrorSchema, "400": ErrorSchema},
)
def add_episodio(form: EpisodioSchema):
    """Adiciona um novo episódio à base de dados
    Retorna uma representação do episódio
    """
    episodio = Episodio(
        titulo=form.titulo,
        audio=form.audio,
        capa=form.capa,
        descricao=form.descricao,
    )

    logger.debug("Adicionando episódio de título: %s", episodio.titulo)

    try:
        # criando conexão com a base
        session = Session()
        # adidiconando episódio
        session.add(episodio)
        # efetivando o comando de adição de novo item na tabela
        session.commit()

        logger.debug("Adicionado episódio de título: %s", episodio.titulo)

        return apresenta_episodio(episodio), 200

    except IntegrityError:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Episódio com mesmo título já salvo na base"

        logger.warning("Erro ao adicionar episódio %s, %s", episodio.titulo, error_msg)

        return {"mesage": error_msg}, 409

    except Exception:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar o episódio"

        logger.warning("Erro ao adicionar episódio %s, %s", episodio.titulo, error_msg)

        return {"mesage": error_msg}, 400


@app.get(
    "/episodios/<int:episodio_id>",
    tags=[episodio_tag],
    responses={"200": EpisodioViewSchema, "404": ErrorSchema},
)
def get_episodio(path: EpisodioPath):
    """Faz a busca por um Episodio a partir do id
    Retorna uma representação do episódio
    """
    episodio_id = path.episodio_id

    logger.debug("Buscando dados do episodio com id: %s", episodio_id)

    # criando conexão com a base
    session = Session()

    try:
        # buscando episódio pelo ID
        episodio = session.query(Episodio).filter(Episodio.id == episodio_id).one()
        titulo = episodio.titulo

        logger.debug("Encotrado episódio %s", titulo)

        return apresenta_episodio(episodio), 200

    except NoResultFound:
        error_msg = f"Episódio com ID {episodio_id} não encontrado"

        logger.warning("Erro ao buscar episódio: %s", error_msg)

        return {"message": error_msg}, 404


@app.get(
    "/episodios",
    tags=[episodio_tag],
    responses={"200": EpisodioViewSchema, "404": ErrorSchema},
)
def list_episodios():
    """Faz a busca por todos os Episodio cadastrados
    Retorna uma representação da listagem de episódios.
    """
    logger.debug("Buscando episódios")

    # criando conexão com a base
    session = Session()
    # fazendo a busca
    episodios = session.query(Episodio).order_by(Episodio.data_insercao.desc()).all()

    if not episodios:
        # se não há episodios cadastrados
        return {"episodios": []}, 200
    else:
        logger.debug("%d episodios econtrados", len(episodios))
        # retorna a representação de produto
        print(episodios)
        return apresenta_episodios(episodios), 200


@app.delete(
    "/episodios/<int:episodio_id>",
    tags=[episodio_tag],
    responses={"200": EpisodioDelSchema, "404": ErrorSchema},
)
def delete_episodio(path: EpisodioPath):
    """
    Deleta um episódio com o ID usado
    Retorna uma mensagem de confirmação da remoção

    - **episodio_id**: ID do episódio a ser deletado.
    """
    episodio_id = path.episodio_id

    logger.debug("Deletando dados do episodio com id: %s", episodio_id)

    # criando conexão com a base
    session = Session()

    try:
        # buscando episódio pelo ID
        episodio = session.query(Episodio).filter(Episodio.id == episodio_id).one()
        titulo = episodio.titulo

        # deletando episódio
        session.delete(episodio)
        session.commit()

        logger.debug("Deletado episódio %s", titulo)

        return {"message": "Episódio removido", "id": episodio_id, "titulo": titulo}

    except NoResultFound:
        error_msg = f"Episódio com ID {episodio_id} não encontrado"

        logger.warning("Erro ao deletar episódio: %s", error_msg)

        return {"message": error_msg}, 404


@app.put(
    "/episodios/<int:episodio_id>",
    tags=[episodio_tag],
    responses={"200": EpisodioViewSchema, "404": ErrorSchema},
)
def update_episodio(path: EpisodioPath, form: EpisodioSchema):
    """Atualiza um Episodio a partir do id
    Retorna uma representação do episódio atualizado
    """
    episodio_id = path.episodio_id

    logger.debug("Atualizando dados do episodio com id: %s", episodio_id)

    # criando conexão com a base
    session = Session()

    try:
        # buscando episódio pelo ID
        episodio = (
            session.query(Episodio).filter(Episodio.id == episodio_id).one_or_none()
        )

        # se não encontrou episódio retorna erro
        if not episodio:
            error_msg = f"Episódio com ID {episodio_id} não encontrado"
            logger.warning("Erro ao atualizar episódio: %s", error_msg)
            return {"message": error_msg}, 404

        # atualizando informações do episódio
        episodio.titulo = form.titulo
        episodio.audio = form.audio
        episodio.capa = form.capa
        episodio.descricao = form.descricao

        session.commit()

        logger.debug("Atualizado episódio com id %s", episodio_id)
        return apresenta_episodio(episodio), 200

    # trata erro inesperado na atualização
    except Exception as e:
        # reverte em caso de erro
        session.rollback()
        error_msg = f"Erro ao atualizar episódio com id {episodio_id}: {str(e)}"
        logger.error(error_msg)
        return {"message": error_msg}, 400

    finally:
        session.close()


## PROFILE
@app.post(
    "/profile",
    tags=[profile_tag],
    responses={
        "200": ProfileSchema,
        "409": ErrorSchema,
        "400": ErrorSchema,
        "405": ErrorSchema,
    },
)
def add_profile(form: ProfileSchema):
    """Adiciona um novo Profile à base de dados
    Retorna uma representação do profile
    """
    profile = Profile(
        nome=form.nome,
        autor=form.autor,
        descricao=form.descricao,
        capa=form.capa,
    )

    logger.debug("Adicionando profile do podcast: %s", profile.nome)

    try:
        # criando conexão com a base
        session = Session()

        if (session.query(Profile).count() > 0):
            error_msg = "Não é permitido criar mais de um profile"
            return {"mesage": error_msg}, 405

        # adidiconando profile
        session.add(profile)
        # efetivando o comando de adição de novo item na tabela
        session.commit()

        logger.debug("Adicionado profile de nome: %s", profile.nome)

        return apresenta_profile(profile), 200

    except IntegrityError:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Profile com mesmo nome já salvo na base"

        logger.warning("Erro ao adicionar profile %s, %s", profile.nome, error_msg)

        return {"mesage": error_msg}, 409

    except Exception:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar o profile"

        logger.warning("Erro ao adicionar profile %s, %s", profile.nome, error_msg)

        return {"mesage": error_msg}, 400


@app.get(
    "/profile",
    tags=[profile_tag],
    responses={"200": ProfileSchema, "404": ErrorSchema},
)
def get_profile():
    """Retorna o profile cadastrado.
    """
    logger.debug("Buscando profile")

    # criando conexão com a base
    session = Session()
    # fazendo a busca
    profile = session.query(Profile).first()

    if not profile:
        # se não há profile cadastrado
        return {}, 200

    logger.debug("%d profile econtrado", profile)
    # retorna a representação de produto
    print(profile)
    return apresenta_profile(profile), 200


@app.delete(
    "/profile",
    tags=[profile_tag],
    responses={"200": ProfileDelSchema, "404": ErrorSchema},
)
def delete_profile():
    """
    Deleta o profile
    Retorna uma mensagem de confirmação da remoção
    """
    try:
        # criando conexão com a base
        session = Session()

        logger.debug("Deletando profile")

        # buscando profile
        profile = session.query(Profile).first()

        if not profile:
            error_msg = "Nenhum profile encontrado para deletar"

            logger.warning("Erro ao deletar profile: %s", error_msg)

            return {"message": error_msg}, 404

        nome = profile.nome

        # deletando profile
        session.delete(profile)
        session.commit()

        logger.debug("Deletado profile %s", nome)

        return {"message": "Profile removido", "id": profile.id, "nome": profile.nome}

    except Exception:
        # caso um erro fora do previsto
        error_msg = "Não foi possível deletar o profile"

        logger.warning("Erro ao deletar profile %s, %s", profile.nome, error_msg)

        return {"mesage": error_msg}, 400
