from sqlalchemy import Column, Integer, String, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() 
class Shard(Base):
    """
    Sharding table
    """
    __tablename__ = "shard"
    id     = Column(Integer, autoincrement=True, primary_key=True)
    kind   = Column(String(256))
    bucket = Column(String(256))
    name   = Column(String(256))
    UniqueConstraint(kind, name)
    Index('shard_kind_name_index', kind, name)

    def __repr__(self):
        return f'<User(id={self.id}, kind={self.kind}, bucket={self.bucket}, name={self.name})>'

if __name__ == "__main__":
    from sqlalchemy import create_engine, func
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:///:memory:', echo=True)

    Base.metadata.create_all(engine)


    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    session.add(Shard(kind='hub', bucket='hub-1', name='dummy-1'))
    session.add(Shard(kind='hub', bucket='hub-1', name='dummy-2'))
    session.add(Shard(kind='hub', bucket='hub-1', name='dummy-3'))
    session.add(Shard(kind='hub', bucket='hub-2', name='dummy-4'))
    session.add(Shard(kind='hub', bucket='hub-2', name='dummy-5'))
    session.add(Shard(kind='hub', bucket='hub-3', name='dummy-6'))
    session.add(Shard(kind='hub', bucket='hub-3', name='dummy-7'))
    session.add(Shard(kind='hub', bucket='hub-3', name='dummy-8'))
    session.add(Shard(kind='hub', bucket='hub-3', name='dummy-9'))

    session.commit()

    #q = session.query(Shard).filter(Shard.kind == 'hub').first()
    #print(q)
    #q = session.query(Shard).filter(Shard.kind == 'hub').group_by(Shard.bucket).count()
    #print(q)
    #q = session.query(Shard).filter(Shard.kind == 'hub').group_by(Shard.bucket).statement.with_only_columns([func.count()]).order_by(None)
    #l = session.execute(q).scalar()
    #print(f'Here is the session execution result {l}')


    emptiest_bucket = (session.query(Shard, func.count(Shard.bucket)
        .label('total'))
        .filter(Shard.kind == 'hub')
        .group_by(Shard.bucket)
        .order_by('total').first()
    )
    if emptiest_bucket:
        print('Please use {} - it is the emptiest bucket currently'.format(emptiest_bucket[0].bucket))
