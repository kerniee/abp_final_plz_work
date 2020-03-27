import sqlalchemy

from .db_session import SqlAlchemyBase


class Orders(SqlAlchemyBase):
    __tablename__ = 'Orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    createDate = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    closeDate = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    costumer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    dron_lst = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    state = sqlalchemy.Column(sqlalchemy.String, nullable=True)
