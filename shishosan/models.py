from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    Unicode,
    ForeignKey,
)
from sqlalchemy.orm import (
    relationship,
)

from passlib.context import CryptContext

from .db import (
    Base,
    DBSession,
)


class User(Base):
    __tablename__ = 'users'
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)

    name = Column(Text, unique=True)
    _password = Column(String, nullable=False)
    _password_ctx = CryptContext(["sha512_crypt"])

    def __init__(self, name, password):
        self.name = name
        self.set_password(password)
        # TODO: validate that name should be ascii

    def set_password(self, password):
        """set password with hashing
        :param password: raw new password
        :type password: str
        :return: None
        """
        self._password = self._password_ctx.encrypt(password)

    def verify_password(self, password):
        """verify password. return it is correct, or not;
        :param password:  raw password, user inputs.
        :type password: str
        :return is correct the password.
        :rtype: bool
        """
        return self._password_ctx.verify(password, self._password)

    def add_bookmark(self, novel):
        """
        :type novel: Novel
        :rtype: Bookmark
        """
        return Bookmark(self, novel)


class Novel(Base):
    __tablename__ = 'novels'
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)

    name = Column(Unicode)
    site_name = Column(String)
    pattern_url = Column(String)

    def __init__(self, name, patter_url):
        self.name = name
        self.pattern_url = patter_url


class Bookmark(Base):
    __tablename__ = 'bookmarks'
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    uesr = relationship(User)

    novel_id = Column(Integer, ForeignKey('novels.id'))
    novel = relationship(Novel)

    state = Column(Integer, nullable=False, default=0)
    url = Column(String)

    def __init__(self, user, novel):
        self.user = user
        self.novel = novel


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)


Index('my_index', MyModel.name, unique=True, mysql_length=255)
