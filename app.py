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
from schemas.importacao import ImportacaoFeedSchema, ImportacaoFeedViewSchema
from schemas.profile import (
    ProfileSchema,
    ProfileViewSchema,
    apresenta_profile,
    ProfileDelSchema,
)

info = Info(title="Poscast API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# Definindo tags

# Tag para seleção da documentação
home_tag = Tag(
    name="Documentação",
    description="Seleção de documentação: Swagger, Redoc ou RapiDoc",
)

# Tag para endpoints que controlam a entidade Episodio
episodio_tag = Tag(
    name="Episódio",
    description="Adição, visualização,atualização e remoção de episódios de podcast à base",
)

# Tag para endpoints que controlam a entidade Profile
profile_tag = Tag(
    name="Profile",
    description="Adição, visualização e deleção do profile/perfil do podcast",
)

# Tag para endpoints que fazem importação
importacao_tag = Tag(
    name="Importação",
    description="Importação de profile e episódios via feed rss do podcast",
)


@app.get("/", tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação."""
    return redirect("/openapi")


# Endpoints para Episodio
@app.post(
    "/episodios",
    tags=[episodio_tag],
    responses={"200": EpisodioSchema, "409": ErrorSchema, "400": ErrorSchema},
)
def add_episodio(form: EpisodioSchema):
    """Adiciona um novo Episodio à base de dados
    Retorna uma representação do Episodio criado
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

        return {"message": error_msg}, 409

    except Exception:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar o episódio"

        logger.warning("Erro ao adicionar episódio %s, %s", episodio.titulo, error_msg)

        return {"message": error_msg}, 400


@app.get(
    "/episodios/<int:episodio_id>",
    tags=[episodio_tag],
    responses={"200": EpisodioViewSchema, "404": ErrorSchema},
)
def get_episodio(path: EpisodioPath):
    """Faz a busca por um Episodio a partir do id
    Retorna uma representação do Episodio
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
        # se não encontrou o episódio ao buscar pelo `one()`
        error_msg = f"Episódio com ID {episodio_id} não encontrado"

        logger.warning("Erro ao buscar episódio: %s", error_msg)

        return {"message": error_msg}, 404

    except Exception:
        # caso um erro fora do previsto
        error_msg = "Não foi possível encontrar o episódio"

        logger.warning("Erro ao buscar episódio com ID %s, %s", episodio_id, error_msg)

        return {"message": error_msg}, 400


@app.get(
    "/episodios",
    tags=[episodio_tag],
    responses={"200": EpisodioViewSchema, "404": ErrorSchema},
)
def list_episodios():
    """Faz a busca por todos os Episodio cadastrados
    Retorna uma representação da listagem de Episodios encontradas.
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

        # retorna a representação dos Episodio
        return apresenta_episodios(episodios), 200


@app.delete(
    "/episodios/<int:episodio_id>",
    tags=[episodio_tag],
    responses={"200": EpisodioDelSchema, "404": ErrorSchema},
)
def delete_episodio(path: EpisodioPath):
    """
    Deleta um Episodio com o ID usado
    Retorna uma mensagem de confirmação da remoção
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
        # se não encontrou o episódio ao buscar pelo `one()`
        error_msg = f"Episódio com ID {episodio_id} não encontrado"

        logger.warning("Erro ao deletar episódio: %s", error_msg)

        return {"message": error_msg}, 404

    except Exception:
        # caso um erro fora do previsto
        error_msg = "Não foi possível deletar o episódio"

        logger.warning("Erro ao deletar episódio com ID %s, %s", episodio_id, error_msg)

        return {"message": error_msg}, 400


@app.put(
    "/episodios/<int:episodio_id>",
    tags=[episodio_tag],
    responses={"200": EpisodioViewSchema, "404": ErrorSchema},
)
def update_episodio(path: EpisodioPath, form: EpisodioSchema):
    """Atualiza um Episodio a partir do id
    Retorna uma representação do Episodio atualizado
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


# Endpoints para Profile
@app.post(
    "/profile",
    tags=[profile_tag],
    responses={
        "200": ProfileViewSchema,
        "400": ErrorSchema,
        "405": ErrorSchema,
    },
)
def add_profile(form: ProfileSchema):
    """Adiciona um novo Profile à base de dados
    Retorna uma representação do Profile
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

        # verifica se já existe um perfil cadastrado, é limitado a 1
        if session.query(Profile).count() > 0:
            error_msg = "Não é permitido criar mais de um profile"
            return {"message": error_msg}, 405

        # adidiconando profile
        session.add(profile)
        # efetivando o comando de adição de novo item na tabela
        session.commit()

        logger.debug("Adicionado profile de nome: %s", profile.nome)

        return apresenta_profile(profile), 200

    except Exception:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar o profile"

        logger.warning("Erro ao adicionar profile %s, %s", profile.nome, error_msg)

        return {"message": error_msg}, 400


@app.get(
    "/profile",
    tags=[profile_tag],
    responses={"200": ProfileViewSchema, "404": ErrorSchema},
)
def get_profile():
    """Faz a busca pelo Profile único permitido
    Retorna uma representação do Episodio
    """
    logger.debug("Buscando profile")

    # criando conexão com a base
    session = Session()

    # busca Profile para vê se já está cadastrado
    profile = session.query(Profile).first()

    if not profile:
        # se não há Profile cadastrado
        return {}, 200

    logger.debug("%d profile econtrado", profile)

    # retorna a representação do Profile
    return apresenta_profile(profile), 200


@app.delete(
    "/profile",
    tags=[profile_tag],
    responses={"200": ProfileDelSchema, "404": ErrorSchema},
)
def delete_profile():
    """
    Deleta um Profile
    Retorna uma mensagem de confirmação da remoção
    """
    try:
        # criando conexão com a base
        session = Session()

        logger.debug("Deletando profile")

        # buscando profile
        profile = session.query(Profile).first()

        # retorna erro se não encontrou um Profile para deletar
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

        return {"message": error_msg}, 400


@app.post(
    "/importacoes/feed-rss",
    tags=[importacao_tag],
    responses={"200": ImportacaoFeedViewSchema, "400": ErrorSchema},
)
def importar_rss(form: ImportacaoFeedSchema):
    rss_feed_url = form.feed

    session = Session()

    # cria uma lista para mandar todo os erros encontrados durante a importação
    erros_encontrados = []

    try:
        # faz a análise do rss_feed
        feed = feedparser.parse(rss_feed_url)

        # se não encontrou um título, o feed não é compatível
        if not feed or "title" not in feed.feed:
            return {"message": "Feed RSS inválido ou inacessível"}, 400

        # cria perfil com o padrão do rss_feed
        profile = Profile(
            nome=feed.channel.title,
            autor=feed.channel.author,
            descricao=feed.channel.summary,
            capa=feed.channel.image.href,
        )

        # adiciona Profile caso ainda não exista um
        if session.query(Profile).count() == 0:
            try:
                # adidiconando profile
                session.add(profile)
                # efetivando o comando de adição de novo item na tabela
                session.commit()

                logger.debug("Adicionado profile de nome: %s", profile.nome)

            except Exception:
                # caso um erro fora do previsto
                error_msg = "Não foi possível salvar o profile"

                logger.warning(
                    "Erro ao adicionar profile %s, %s", profile.nome, error_msg
                )

                erros_encontrados.append({"message": error_msg})

        # inicia uma lista para salvar todos os Episodio na base
        episodios_no_feed = []

        # Fixando a importação em 10 até desenvolvimento de paginação e player
        for entry in feed.entries[:10]:
            try:
                # busca na base se o episodio já existe
                session.query(Episodio).filter_by(titulo=entry.title).one()

                # se ja existir um episódio com titulo, não adiciona na lista
                # e também joga o erro para a lista específica
                erros_encontrados.append(
                    {"message": f"Episódio com título '{entry.title}' já existe"}
                )

            except NoResultFound:
                # se nao encontrou o episódio, cria um com as informações do
                # feed e adiciona a lista que será adicionada
                # se não tiver uma capa, fica vazio
                episodio = Episodio(
                    titulo=entry.title,
                    descricao=entry.summary,
                    capa=getattr(entry, "image", {}).get("href", ""),
                    audio=entry.links[1].href if len(entry.links) > 1 else "",
                )

                episodios_no_feed.append(episodio)

        # adiciona todos os episodios que já não existiam
        session.add_all(episodios_no_feed)
        session.commit()

        # cria representacao
        return {
            "perfil": apresenta_profile(profile) if profile.data_insercao else {},
            "episodios": (
                apresenta_episodios(episodios_no_feed).get("episodios", [])
                if episodios_no_feed
                else []
            ),
            "erros": erros_encontrados,
        }, 200

    # erro caso o feed não tenha conseguido ser analisado pele feedparser
    except Exception as e:
        return {"message": "Erro ao processar o feed RSS", "error": str(e)}, 400
