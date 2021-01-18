#!/usr/bin/env python3
'''
Database class

MIT License
Copyright (c) 2021 Leboncoin
Written by Yann Faure (yann.faure@adevinta.com)
'''

from .controller.database import DatabaseController

class Database():
    '''Database class'''
    def __init__(self, dbname):
        self.database = DatabaseController(dbname)

    def init_databases(self):
        '''Create databases if not presents and init data'''
        self.database.exec('CREATE TABLE IF NOT EXISTS trademarks \
            (id INTEGER PRIMARY KEY, trademark TEXT NOT NULL);')
        self.database.exec('CREATE TABLE IF NOT EXISTS keywords \
            (id INTEGER PRIMARY KEY, id_trademark INTEGER NOT NULL, keyword TEXT NOT NULL);')

    # Trademarks
    def get_trademarks(self):
        '''Get trademarks'''
        return self.database.fetchall('SELECT id, trademark from trademarks')

    def insert_trademark(self, trademark):
        '''Insert trademark'''
        self.database.exec('INSERT INTO trademarks(trademark) \
                        VALUES (?);',(trademark,))

    def delete_trademark(self, id_trademark):
        '''Delete trademark'''
        self.database.exec('DELETE FROM trademarks WHERE id = ?', (id_trademark,))

    def update_trademark(self, id_trademark, new_trademark_name):
        '''Update trademark'''
        self.database.exec('UPDATE trademarks SET trademark = ? WHERE id = ?',
                            (new_trademark_name, id_trademark,))

    def get_trademark_by_id(self, id_trademark):
        '''Get trademark by id'''
        return self.database.fetchall('SELECT id, trademark from trademarks WHERE id = ?',
                            (id_trademark,))

    # Keywords
    def get_keyword_by_id(self, id_keyword):
        '''Get keyword by id'''
        return self.database.fetchall('SELECT id, id_trademark, keyword FROM keywords \
                            WHERE id = ?', (id_keyword,))

    def get_keywords_by_trademark_id(self, id_trademark):
        '''Get keywords by trademark id'''
        return self.database.fetchall('SELECT id, id_trademark, keyword from keywords \
                            WHERE id_trademark = ?', (id_trademark,))

    def insert_keyword(self, id_trademark, keyword):
        '''Insert keyword'''
        self.database.exec('INSERT INTO keywords(id_trademark, keyword) \
                        VALUES (?, ?)', (id_trademark, keyword,))

    def delete_keyword(self, id_keyword):
        '''Delete keyword'''
        self.database.exec('DELETE FROM keywords WHERE id = ?', (id_keyword,))

    def update_keyword(self, id_keyword, new_keyword_name):
        '''Update keyword'''
        self.database.exec('UPDATE keywords SET keyword = ? WHERE id = ?',
                            (new_keyword_name, id_keyword,))
