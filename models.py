from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    breaks = relationship("Break", back_populates="location", cascade="all, delete-orphan", order_by="Break.start_time")


class Break(Base):
    __tablename__ = "breaks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_time = Column(String, nullable=False)  # "HH:MM"
    end_time = Column(String, nullable=False)    # "HH:MM"
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

    location = relationship("Location", back_populates="breaks")
