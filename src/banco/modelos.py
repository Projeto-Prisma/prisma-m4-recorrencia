import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()


class CategoriaDenuncia(str, enum.Enum):
    # Infraestrutura
    BURACO_VIA = "BURACO_VIA"
    CALCADA_IRREGULAR = "CALCADA_IRREGULAR"
    VIA_CEDENDO = "VIA_CEDENDO"

    # Iluminação e Energia
    ILUMINACAO_PUBLICA = "ILUMINACAO_PUBLICA"  # Poste apagado ou piscando
    FIO_ROMPIDO = "FIO_ROMPIDO"
    POSTE_EM_RISCO = "POSTE_EM_RISCO"

    # Saneamento 
    VAZAMENTO_AGUA = "VAZAMENTO_AGUA"
    VAZAMENTO_ESGOTO = "VAZAMENTO_ESGOTO"
    BUEIRO_ENTUPIDO = "BUEIRO_ENTUPIDO"

    # Limpeza Urbana
    LIXO_IRREGULAR = "LIXO_IRREGULAR"
    ENTULHO_CALCADA = "ENTULHO_CALCADA"
    ANIMAL_MORTO = "ANIMAL_MORTO"

    # Meio Ambiente e Defesa Civil
    ARVORE_RISCO_QUEDA = "ARVORE_RISCO_QUEDA"
    PODA_ARVORE = "PODA_ARVORE"
    FOCO_DENGUE = "FOCO_DENGUE"
    ALAGAMENTO = "ALAGAMENTO"

    # Mobilidade
    SEMAFORO_QUEBRADO = "SEMAFORO_QUEBRADO"
    SINALIZACAO_DANIFICADA = "SINALIZACAO_DANIFICADA"
    VEICULO_ABANDONADO = "VEICULO_ABANDONADO"
    
    OUTROS = "OUTROS"


class Denuncia(Base):
    __tablename__ = "denuncias"

    id = Column(Integer, primary_key=True, index=True)
    # O banco só aceita o que está no Enum
    categoria = Column(Enum(CategoriaDenuncia), nullable=False)
    data_ocorrencia = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    localizacao = Column(Geometry("POINT", srid=4326), nullable=False)

    # Gera um UUID único, mas pode ser sobrescrito se for recorrente
    cluster_id = Column(
        String, index=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
