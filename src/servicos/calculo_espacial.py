import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.elements import WKTElement

from src.banco.modelos import Denuncia, CategoriaM2

CONFIGURACAO_RECORRENCIA = {
    # LIMPEZA E CONSERVAÇÃO
    CategoriaM2.DESCARTE_IRREGULAR: {"raio_metros": 30.0, "janela_dias": 15},
    CategoriaM2.COLETA_LIXO: {"raio_metros": 50.0, "janela_dias": 7},
    CategoriaM2.MANUTENCAO_LIMPEZA: {"raio_metros": 40.0, "janela_dias": 30},
    # INFRAESTRUTURA EXTERNA
    CategoriaM2.COMPESA: {"raio_metros": 50.0, "janela_dias": 15},
    # MEIO AMBIENTE E SAÚDE
    CategoriaM2.POLUICAO_SONORA: {"raio_metros": 150.0, "janela_dias": 3},
    CategoriaM2.POLUICAO: {"raio_metros": 200.0, "janela_dias": 30},
    CategoriaM2.VIGILANCIA_AMBIENTAL: {"raio_metros": 100.0, "janela_dias": 45},
    CategoriaM2.VIGILANCIA_SANITARIA: {"raio_metros": 50.0, "janela_dias": 15},
    # FISCALIZAÇÃO URBANA E OBRAS
    CategoriaM2.COMERCIO_INFORMAL: {"raio_metros": 20.0, "janela_dias": 7},
    CategoriaM2.CONSTRUCAO_IRREGULAR: {"raio_metros": 20.0, "janela_dias": 90},
    CategoriaM2.IMOVEL_ABANDONADO: {"raio_metros": 20.0, "janela_dias": 180},
    CategoriaM2.INVASAO: {"raio_metros": 50.0, "janela_dias": 30},
    # MOBILIDADE
    CategoriaM2.ESTACIONAMENTO: {"raio_metros": 30.0, "janela_dias": 5},
    CategoriaM2.TRIAGEM_GERAL: {"raio_metros": 50.0, "janela_dias": 30},
    # DEFAULT
    "default": {"raio_metros": 10.0, "janela_dias": 7},
}


def processar_nova_denuncia(
    db: Session, latitude: float, longitude: float, categoria_texto: str
) -> dict:

    categoria = CategoriaM2(categoria_texto)
    regra = CONFIGURACAO_RECORRENCIA.get(categoria, CONFIGURACAO_RECORRENCIA["default"])
    janela_dias = regra["janela_dias"]
    raio_metros = regra["raio_metros"]

    data_limite = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        days=janela_dias
    )
    ponto_wkt = f"POINT({longitude} {latitude})"
    ponto_geografico = WKTElement(ponto_wkt, srid=4326)

    denuncia_relacionada = (
        db.query(Denuncia)
        .filter(
            Denuncia.categoria == categoria,
            ST_DWithin(
                Denuncia.localizacao,
                func.ST_GeomFromText(ponto_wkt, 4326),
                raio_metros,
                True,
            ),
            or_(Denuncia.resolvido == False, Denuncia.data_ocorrencia >= data_limite),
        )
        .order_by(Denuncia.data_ocorrencia.asc())
        .first()
    )

    if denuncia_relacionada:
        novo_cluster_id = denuncia_relacionada.cluster_id
    else:
        novo_cluster_id = str(uuid.uuid4())

    nova_denuncia = Denuncia(
        categoria=categoria,
        localizacao=ponto_geografico,
        cluster_id=novo_cluster_id,
        resolvido=False,
    )
    db.add(nova_denuncia)
    db.commit()
    db.refresh(nova_denuncia)

    contagem_historica = (
        db.query(func.count(Denuncia.id))
        .filter(
            Denuncia.cluster_id == novo_cluster_id,
            or_(Denuncia.resolvido == False, Denuncia.data_ocorrencia >= data_limite),
        )
        .scalar()
    )

    return {
        "evento": "padrao.recorrencia",
        "payload": {
            "regiao": {
                "cluster_id": novo_cluster_id,
                "centroide": {"latitude": latitude, "longitude": longitude},
            },
            "categoria": categoria.value,
            "contagem": contagem_historica,
            "janela_de_tempo": f"{janela_dias} dias",
        },
    }
