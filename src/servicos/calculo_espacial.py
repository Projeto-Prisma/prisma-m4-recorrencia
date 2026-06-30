import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.elements import WKTElement

from src.banco.modelos import Denuncia, CategoriaDenuncia

# Configuração (Regras Dinâmicas)
CONFIGURACAO_RECORRENCIA = {
    # INFRAESTRUTURA: Problemas muito pontuais. Raio curto.
    CategoriaDenuncia.BURACO_VIA: {"raio_metros": 15.0, "janela_dias": 30},
    CategoriaDenuncia.CALCADA_IRREGULAR: {"raio_metros": 15.0, "janela_dias": 60},
    CategoriaDenuncia.VIA_CEDENDO: {
        "raio_metros": 30.0,
        "janela_dias": 15,
    },  # Urgência maior
    
   
    # ILUMINAÇÃO E ENERGIA: Risco alto e abrange quarteirões.
    CategoriaDenuncia.ILUMINACAO_PUBLICA: {"raio_metros": 50.0, "janela_dias": 15},
    CategoriaDenuncia.FIO_ROMPIDO: {
        "raio_metros": 100.0,
        "janela_dias": 2,
    },  # Altíssima urgência, tempo curto
    CategoriaDenuncia.POSTE_EM_RISCO: {"raio_metros": 30.0, "janela_dias": 7},
    
    
    # SANEAMENTO: Água escorre, então o raio precisa ser um pouco maior.
    CategoriaDenuncia.VAZAMENTO_AGUA: {"raio_metros": 50.0, "janela_dias": 7},
    CategoriaDenuncia.VAZAMENTO_ESGOTO: {"raio_metros": 50.0, "janela_dias": 15},
    CategoriaDenuncia.BUEIRO_ENTUPIDO: {"raio_metros": 30.0, "janela_dias": 30},
    
    # LIMPEZA URBANA: Geralmente confinado a uma esquina ou terreno.
    CategoriaDenuncia.LIXO_IRREGULAR: {"raio_metros": 30.0, "janela_dias": 15},
    CategoriaDenuncia.ENTULHO_CALCADA: {"raio_metros": 20.0, "janela_dias": 15},
    CategoriaDenuncia.ANIMAL_MORTO: {
        "raio_metros": 50.0,
        "janela_dias": 3,
    },  # Rápida decomposição
    
    
    # MEIO AMBIENTE: Raios variados dependendo da biologia/física.
    CategoriaDenuncia.ARVORE_RISCO_QUEDA: {"raio_metros": 20.0, "janela_dias": 5},
    CategoriaDenuncia.PODA_ARVORE: {
        "raio_metros": 50.0,
        "janela_dias": 90,
    },  # Poda dura meses para precisar de novo
    CategoriaDenuncia.FOCO_DENGUE: {
        "raio_metros": 300.0,
        "janela_dias": 30,
    },  # O mosquito voa em média 300m
    CategoriaDenuncia.ALAGAMENTO: {
        "raio_metros": 300.0,
        "janela_dias": 365,
    },  # Sazonalidade anual
    
    
    # TRÂNSITO: Cruzamentos são exatos.
    CategoriaDenuncia.SEMAFORO_QUEBRADO: {"raio_metros": 30.0, "janela_dias": 3},
    CategoriaDenuncia.SINALIZACAO_DANIFICADA: {"raio_metros": 20.0, "janela_dias": 30},
    CategoriaDenuncia.VEICULO_ABANDONADO: {"raio_metros": 15.0, "janela_dias": 45},
    # PADRÃO DE SEGURANÇA
    "default": {"raio_metros": 50.0, "janela_dias": 30},
}


def processar_nova_denuncia(
    db: Session, latitude: float, longitude: float, categoria: CategoriaDenuncia
) -> dict:
    """
    Analisa uma nova denúncia, verifica recorrências espaciais e a salva no banco.
    Retorna um dicionário com os dados da denúncia e se ela é um alerta recorrente.
    """
    # 1. Resgata a regra da categoria (Usa 'default' se a categoria não estiver na matriz)
    regra = CONFIGURACAO_RECORRENCIA.get(categoria, CONFIGURACAO_RECORRENCIA["default"])

    data_limite = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=regra["janela_dias"])
    ponto_wkt = f"POINT({longitude} {latitude})"
    ponto_geografico = WKTElement(ponto_wkt, srid=4326)

    # 2. São buscados padrões já cadastrados no banco usando PostGIS
    denuncia_relacionada = (
        db.query(Denuncia)
        .filter(
            Denuncia.categoria == categoria,
            Denuncia.data_ocorrencia >= data_limite,
            ST_DWithin(
                Denuncia.localizacao,
                func.ST_GeomFromText(ponto_wkt, 4326),
                regra["raio_metros"],
                True,  # Usa a curvatura da Terra para cálculo exato em metros
            ),
        )
        .order_by(Denuncia.data_ocorrencia.asc())
        .first()
    )

    # 3. Lógica de Negócio (Clusterização)
    is_recorrente = False
    if denuncia_relacionada:
        novo_cluster_id = denuncia_relacionada.cluster_id
        is_recorrente = True
    else:
        novo_cluster_id = str(uuid.uuid4())

    # 4. Salva a nova denúncia herdando o cluster ou criando um novo
    nova_denuncia = Denuncia(
        categoria=categoria, localizacao=ponto_geografico, cluster_id=novo_cluster_id
    )

    db.add(nova_denuncia)
    db.commit()
    db.refresh(nova_denuncia)

    return {
        "denuncia_id": nova_denuncia.id,
        "cluster_id": nova_denuncia.cluster_id,
        "is_recorrente": is_recorrente,
        "categoria": categoria.value,
    }
