from sqlalchemy import Integer, String, Column, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from . import Base
from .user import User
from sqlalchemy.schema import ForeignKey
from flask import current_app as capp

class Client(Base):
    __tablename__ = "client"

    # human readable name, not required
    name = Column(String(40))

    # human readable description, not required
    description = Column(String(400))

    # required if you need to support client credential
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User', backref='clients')

    client_id = Column(String(40), primary_key=True)
    # this is hashed secret
    client_secret = Column(String(55), unique=True, index=True,
                           nullable=False)

    # public or confidential
    is_confidential = Column(Boolean)

    _redirect_uris = Column(Text)
    _default_scopes = Column(Text)
    _scopes = ['compute', 'storage']
    allowed_grant_types = ["authorization_code"]
    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

    def validate_scopes(self, scopes):
        print scopes
        print self._scopes
        return all(scope in self._scopes for scope in scopes)


class Grant(Base):
    __tablename__ = "grant"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer, ForeignKey(User.id, ondelete='CASCADE')
    )
    user = relationship('User', backref="grants", lazy='subquery')

    client_id = Column(
        String(40), ForeignKey('client.client_id'),
        nullable=False,
    )
    client = relationship('Client', backref='grants')

    code = Column(String(255), index=True, nullable=False)

    redirect_uri = Column(String(255))
    expires = Column(DateTime)

    _scopes = Column(Text)

    def delete(self):
        with capp.db.session as session:
            session.delete(self)
            session.commit()
            return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(Base):
    __tablename__ = "token"

    id = Column(Integer, primary_key=True)
    client_id = Column(
        String(40), ForeignKey('client.client_id'),
        nullable=False,
    )
    client = relationship('Client')

    user_id = Column(
        Integer, ForeignKey(User.id)
    )
    user = relationship('User')

    # currently only bearer is supported
    token_type = Column(String(40))

    access_token = Column(String(255), unique=True)
    refresh_token = Column(String(255), unique=True)
    expires = Column(DateTime)
    _scopes = Column(Text)

    def delete(self):
        with capp.db.session as session:
            session.delete(self)
            session.commit()
            return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []
