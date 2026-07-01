import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()


class CategoriaM2(str, enum.Enum):
    # Meio Ambiente e Sustentabilidade
    CRIME_AMBIENTAL = "Crime Ambiental"
    POLUICAO = "Poluição"
    POLUICAO_SONORA = "Poluição Sonora"
    VIGILANCIA_AMBIENTAL = "Vigilância Ambiental"

    # Limpeza e Conservação Urbana
    COLETA_LIXO = "Coleta de Lixo"
    DESCARTE_IRREGULAR = "Descarte Irregular de Lixo"
    MANUTENCAO_LIMPEZA = "Manutenção e Limpeza Urbana"

    # Saúde
    AGENTE_SAUDE = "Agente de Saúde"
    CONDUTA_MEDICA = "Conduta Médica"
    SAUDE_RECIFE = "Saúde Recife"
    UNIDADES_SAUDE = "Unidades de Saúde"
    VIGILANCIA_SANITARIA = "Vigilância Sanitária"

    # Educação e Esporte
    ACADEMIA_RECIFE = (
        "Academia  Recife"  # Mantendo o espaço duplo original do modelo M2
    )
    ACADEMIA_CIDADE = "Academia da Cidade"
    CRECHE = "Creche"
    PROFESSOR = "Professor"

    # Proteção e Direitos Humanos
    ACESSIBILIDADE = "Acessibilidade"
    AGRESSAO = "Agressão"
    ASSEDIO = "Assédio"
    CASA_APOIO = "Casa de Apoio"
    CONSELHO_TUTELAR = "Conselho Tutelar"
    CRIANCA_ADOLESCENTE = "Criança e Adolescente"
    POPULACAO_RUA = "População em Situação de Rua"
    VIOLACAO_DIREITOS = "Violação de Direitos"
    VIOLACAO_DIREITO_IDOSO = "Violação do Direito do Idoso"
    VIOLENCIA_IDOSO = "Violência contra a Pessoa Idosa"
    VIOLENCIA_PCD = "Violência contra a Pessoa com Deficiência"

    # Fiscalização e Ordem Pública
    COMERCIO_INFORMAL = "Comercio Informal"
    CONSTRUCAO_IRREGULAR = "Construção Irregular"
    FISCALIZACAO = "Fiscalização"
    IMOVEL_ABANDONADO = "Imóvel abandonado"
    INVASAO = "Invasão"
    VISTORIA = "Vistoria"

    # Mobilidade e Trânsito
    ESTACIONAMENTO = "Estacionamento"
    LINHA_COMPLEMENTAR = "Linha Complementar"
    REBOQUE = "Reboque"
    TAXI = "Táxi"

    # Defesa Animal
    DIREITOS_ANIMAIS = "Direitos Animais"

    # Integridade e Conduta Pública
    ABUSO_AUTORIDADE = "Abuso de Autoridade"
    ACUMULACAO_CARGOS = "Acumulação Indevida de Cargos Públicos"
    ASSEDIO_MORAL = "Assédio Moral"
    ATO_LESIVO = "Ato lesivo contra a Administração Pública"
    CONDUTA_ANTIETICA = "Conduta Antiética"
    CONDUTA_INAPROPRIADA = "Conduta Inapropriada"
    CORRUPCAO = "Corrupção"
    GESTAO = "Gestão"
    IRREGULARIDADE_ADMINISTRATIVA = "Irregularidade Administrativa"
    IRREGULARIDADE_ADMIN_MIN = "Irregularidade administrativa"
    IRREGULARIDADES_ADMIN_PLURAL = "Irregularidades Administrativas"
    PAGAMENTO = "Pagamento"
    PREVARICACAO = "Prevaricação"
    PROCESSO = "Processo"
    SERVIDOR = "Servidor"
    SONEGACAO = "Sonegação"

    # Defesa do Consumidor
    DEFESA_CONSUMIDOR = "Proteção e Defesa do Consumidor"

    # Encaminhamento Externo (Muitas vezes abrange infraestrutura física)
    COMPESA = "Compesa"
    MTE = "Ministério do Trabalho e Emprego"
    SDS = "SDS"
    SES = "SES"

    # Fallback
    TRIAGEM_GERAL = "Triagem Geral"


class Denuncia(Base):
    __tablename__ = "denuncias"

    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(Enum(CategoriaM2), nullable=False)
    data_ocorrencia = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )

    # O SRID 4326 garante que estamos calculando as distâncias baseadas no GPS real (WGS84)
    localizacao = Column(Geometry("POINT", srid=4326), nullable=False)

    # Agrupador do cluster (incidentes idênticos no mesmo tempo/espaço recebem o mesmo ID)
    cluster_id = Column(
        String, index=True, nullable=False, default=lambda: str(uuid.uuid4())
    )

    resolvido = Column(Boolean, default=False, nullable=False, index=True)
