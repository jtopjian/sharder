from tornado import log, web
import tornado.ioloop
import tornado.web

class ShardHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", ShardHandler),
    ])

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sharder import Sharder, Base

    log.enable_pretty_logging()

    # Give ourselves a database to play with. This should probably become an
    # application configuration item e.g. --sqlite, --posgtres. Anything that
    # returns an engine should work
    engine = create_engine('sqlite:///:memory:', echo=True)

    sharder_buckets = [f'hub-{hub}' for hub in range(5)]

    sharder = Sharder(engine, 'hub', sharder_buckets)

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
