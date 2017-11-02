from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'picture': self.picture
            }


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
            }


class Bike(Base):
    __tablename__ = 'bike'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    brand = Column(String(50), nullable=False)
    description = Column(String(), nullable=False)
    imageUrl = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'description': self.description,
            'category': self.category.name
            }


engine = create_engine('sqlite:///bikecatalog.db')
Base.metadata.create_all(engine)
