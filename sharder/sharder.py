from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from db import Shard, Base

class Sharder:
    """
    Simple db based sharder.
    Does least-loaded balancing of a given kind of object (homedirectory, running user, etc)
    across multiple buckets, ensuring that once an object is assigned to a bucket it always
    is assigned to the same bucket.
    """
    def __init__(self, engine, kind, buckets, log):
        self.engine  = engine
        self.kind    = kind
        self.buckets = buckets
        self.log = log

        Base.metadata.create_all(engine, checkfirst=True)

        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()
        
        # Make sure that we have at least one dummy entry for each bucket
        for bucket in buckets:
            if self.session.query(Shard.bucket).filter_by(bucket=bucket, name=f'dummy-{bucket}').scalar() is None:
                self.session.add(Shard(kind=self.kind, bucket=bucket, name=f'dummy-{bucket}'))
                self.session.commit()

    def shard(self, name):
        """
        Return the bucket where name should be placed.

        If it isn't already in the database, a new entry will be created in the
        least populated bucket.
        """
        q = self.session.query(Shard).filter(Shard.kind == self.kind, Shard.name == name).first()
        if q:
            bucket = q.bucket
            print(f'Found {name} sharded into bucket {bucket}')
            return bucket

        # name isn't assigned to a bucket yet, add an entry
        q = (self.session.query(Shard.bucket, func.count(Shard.bucket)
            .label('total'))
            .filter(Shard.kind == self.kind)
            .group_by(Shard.bucket)
            .order_by('total').first()
        )
        if q:
            bucket = q.bucket
        self.session.add(Shard(kind=self.kind, bucket=bucket, name=name))
        self.session.commit()

        return bucket
