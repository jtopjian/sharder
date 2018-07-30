#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
from tornado import log, web, concurrent, gen
import tornado.ioloop
import tornado.web

from sharder import Sharder

class ShardHandler(tornado.web.RequestHandler):
    _sharder_thread_pool = ThreadPoolExecutor(max_workers=1)

    @concurrent.run_on_executor(executor='_sharder_thread_pool')
    def shard(self, username):
        return self.settings['sharder'].shard(username)

    # I can *almost* convince myself that this is OK to be a GET
    @gen.coroutine
    def get(self):
        # This resource is protected so we should see the REMOTE_USER header
        header_name = self.settings['header']
        remote_user = self.request.headers.get(header_name, "")

        if remote_user == "":
            log.app_log.info(f'Failed to find REMOTE_USER')
            raise web.HTTPError(401)

        shard_info = yield self.shard(remote_user)



if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sharder import Sharder, Base

    log.enable_pretty_logging()

    # Give ourselves a database to play with. This should probably become an
    # application configuration item e.g. --sqlite, --posgtres. Anything that
    # returns an engine should work
    # N.B. this doesn't work in :memory: yet, probably because of my session
    # handling
    # engine = create_engine('sqlite:///:memory:', echo=True)
    engine = create_engine('sqlite:///hub.sqlite', echo=True)

    sharder_buckets = [f'hub-{hub}' for hub in range(5)]

    sharder = Sharder(engine, 'hub', sharder_buckets, log.app_log)

    app = web.Application([
        (r"/", ShardHandler),
    ], sharder=sharder, header='REMOTE_USER')

    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
