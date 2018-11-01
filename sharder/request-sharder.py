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
            raise web.HTTPError(401, "Hub sharder unable to find auth headers")

        hub = yield self.shard(remote_user)

        self.set_cookie('hub', hub)
        #self.request.headers['Cookie'] = f'hub={hub}'
        self.redirect(f'/hubs/{hub}')

class HubHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self, hub):
        log.app_log.info('Hub Handler')
        self.render('templates/page.html')

if __name__ == "__main__":
    import getopt
    import os
    import sqlite3
    import sys
    
    from sqlalchemy import create_engine
    from sharder import Sharder, Base

    log.enable_pretty_logging()

    # Give ourselves a database to play with. Anything that returns an engine
    # should work, default to sqlite in memory
    database = 'sqlite' 
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p", ["postgres"])
    except getopt.GetoptError:
        print(f"{sys.argv[0]} [--postgres]")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-p", "--postgres"):
            database = 'postgres'

    if database == 'postgres':
        username = os.environ['POSTGRES_USER']
        password = os.environ['POSTGRES_PASSWORD']
        database = os.environ['POSTGRES_DB']
        engine = create_engine(f'postgresql://{username}:{password}@db/{database}', connect_args={'connect_timeout': 10})
        log.app_log.info(f'Postgresql DB init')
    else:
        ##
        ## sqlite (in memory)
        ##
        # We have to be careful with in memory databases and shared cache, see
        # https://stackoverflow.com/questions/27910829/sqlalchemy-and-sqlite-shared-cache

        ##
        ## postgresql
        ##
        creator = lambda: sqlite3.connect('file::memory:?cache=shared', uri=True)
        engine = create_engine('sqlite://', creator=creator, echo=True)
        log.app_log.info(f'Sqlite3 DB init')
    
    sharder_buckets = [f'hub-{hub}' for hub in range(5)]

    sharder = Sharder(engine, 'hub', sharder_buckets, log.app_log)

    app = web.Application([
        (r"/shard", ShardHandler),
        (r"/hubs/(hub-[0-9]+)", HubHandler),
    ], 
    sharder=sharder, 
    header='REMOTE_USER',
    cookie_secret='__TODO:_GENERATE_A_RANDOM_VALUE_HERE__'
    )
#
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
