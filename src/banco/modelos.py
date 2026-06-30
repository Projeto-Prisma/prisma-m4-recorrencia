from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()


class Denuncia(Base):
    __tablename__ = "denuncias_historico"
    id = Column(Integer, primary_key=True, index=True)

    denuncia_id = Column(String, unique=True, index=True, nullable=False)
    categoria = Column(String, index=True, nullable=False)

    localizacao = Column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False
    )

    data_ocorrencia = Column(DateTime, default=datetime.utcnow, nullable=False)
