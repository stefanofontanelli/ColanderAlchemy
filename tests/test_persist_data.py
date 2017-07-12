import colanderalchemy

from sqlalchemy import (
    event,
    create_engine,
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (sessionmaker, relationship)
from sqlalchemy.engine import Engine

import logging
import sys

if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    # In Python < 2.7 use unittest2.
    import unittest2 as unittest
else:
    import unittest

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Define referential integrity """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    log = logging.getLogger(__name__)
    log.info("PRAGMA foreign_keys=ON")


Base = declarative_base()

class A(Base):
    __tablename__='a'
    id = Column(Integer, primary_key=True)
    v = Column(String())
    
    id_b = Column(Integer, ForeignKey('b.id'))
    bvalue = relationship('B')
    
    cvalues = relationship('C', 
                           secondary='acassociations', 
                           back_populates='avalues')
    
class B(Base):
    __tablename__ = 'b'
    id = Column(Integer, primary_key=True)
    v = String()
    
class C(Base):
    __tablename__ = 'c'
    id = Column(Integer, primary_key=True)
    v = Column(String())
    
    avalues = relationship('A', 
                           secondary='acassociations',
                           back_populates='cvalues')
    
class ACAssociation(Base):
    __tablename__ = 'acassociations'
    id_a = Column(Integer, 
                  ForeignKey('a.id',
                             ondelete='CASCADE',
                             onupdate='CASCADE'),
                  primary_key=True)
                  
    id_c = Column(Integer, 
                  ForeignKey('c.id',
                             ondelete='CASCADE',
                             onupdate='CASCADE'),
                  primary_key=True)
                  

class Tests_persist_relation(unittest.TestCase):
    
    def setUp(self):
        engine = create_engine('sqlite:///:memory:', echo=True)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine)
        
    def tearDown(self):
        self.session.close()
        
    def test_persist_relation(self):
        # create an object
        a_1 = A(v='a_1', bvalue=B(v='b'), cvalues=[C(v='c_1'), C(v='c_2')])
        #a_1 = A(v='a_1',  cvalues=[C(v='c_1'), C(v='c_2')])
        self.session.add(a_1)
        self.session.commit()
        
        # create a SQLAlchemySchemaNode
        schema = colanderalchemy.SQLAlchemySchemaNode(A)
        
        # get data from a_1
        appstruct = schema.dictify(a_1)
        
        # objectify appstruct to a_1
        schema.objectify(appstruct, a_1)
        
        # should not fail        
        self.session.commit()
