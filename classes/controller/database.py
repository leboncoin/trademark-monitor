#!/usr/bin/env python3
'''
Database class

MIT License
Copyright (c) 2021 Leboncoin
Written by Yann Faure (yann.faure@adevinta.com)
'''

import sqlite3

class DatabaseController():
    '''SQLite Database class'''
    def __init__(self, dbname):
        self.dbname = dbname

    def exec(self, req, args=None):
        '''Execute a sql request'''
        conn = sqlite3.connect(self.dbname)
        sql = conn.cursor()
        if args is None:
            sql.execute(req)
        else:
            sql.execute(req, args)
        conn.commit()
        conn.close()

    def fetchall(self, req, args=None):
        '''Execute a sql request and fetchall'''
        conn = sqlite3.connect(self.dbname)
        sql = conn.cursor()
        if args is None:
            sql.execute(req)
        else:
            sql.execute(req, args)
        conn.commit()
        data = sql.fetchall()
        conn.close()
        return data
