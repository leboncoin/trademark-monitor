#!/usr/bin/env python3
'''
Flask APP

MIT License
Copyright (c) 2021 Leboncoin
Written by Yann Faure (yann.faure@adevinta.com)
'''

from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap

from classes.database import Database

database = Database('database.db')
database.init_databases()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    '''root'''
    return render_template('index.html')

@app.route('/trademarks', methods=['GET'])
def trademarks():
    '''trademarks'''
    return render_template('trademarks.html', trademarks=database.get_trademarks())

@app.route('/trademarks/add', methods=['POST'])
def trademarks_add():
    '''trademarks add'''
    database.insert_trademark(request.form['trademark'])
    return render_template('trademarks.html', trademarks=database.get_trademarks())

@app.route('/trademarks/edit/<int:id_trademark>', methods=['GET'])
def trademarks_edit(id_trademark):
    '''trademarks edit'''
    trademarks_all = database.get_trademarks()
    trademark_edit = database.get_trademark_by_id(id_trademark)
    return render_template('trademarks.html',
                trademarks=trademarks_all, trademark_edit=trademark_edit)

@app.route('/trademarks/edit/<int:id_trademark>', methods=['POST'])
def trademarks_edit_id(id_trademark):
    '''trademarks edit id'''
    database.update_trademark(id_trademark, request.form['trademark'])
    trademarks_all = database.get_trademarks()
    trademark_edit = database.get_trademark_by_id(id_trademark)
    return render_template('trademarks.html',
                trademarks=trademarks_all, trademark_edit=trademark_edit)

@app.route('/filters/edit/<int:id_trademark>', methods=['GET'])
def filters(id_trademark):
    '''filters by trademark id'''
    trademark = database.get_trademark_by_id(id_trademark)
    keywords = database.get_keywords_by_trademark_id(id_trademark)
    return render_template('filters.html', trademark=trademark, keywords=keywords)

@app.route('/trademark/<int:id_trademark>/keywords/add', methods=['POST'])
def keywords_add(id_trademark):
    '''keywords add'''
    database.insert_keyword(id_trademark, request.form['keyword'])
    trademark = database.get_trademark_by_id(id_trademark)
    keywords = database.get_keywords_by_trademark_id(id_trademark)
    return render_template('filters.html', trademark=trademark, keywords=keywords)

@app.route('/trademark/<int:id_trademark>/keywords/edit/<int:id_keyword>', methods=['GET'])
def keywords_edit(id_trademark, id_keyword):
    '''keywords edit'''
    trademark = database.get_trademark_by_id(id_trademark)
    keywords = database.get_keywords_by_trademark_id(id_trademark)
    keyword_edit = database.get_keyword_by_id(id_keyword)
    return render_template('filters.html',
                trademark=trademark, keywords=keywords, keyword_edit=keyword_edit)

@app.route('/trademark/<int:id_trademark>/keywords/edit/<int:id_keyword>', methods=['POST'])
def keywords_edit_id(id_trademark, id_keyword):
    '''keyword edit id'''
    database.update_keyword(id_keyword, request.form['keyword'])
    trademark = database.get_trademark_by_id(id_trademark)
    keywords = database.get_keywords_by_trademark_id(id_trademark)
    keyword_edit = database.get_keyword_by_id(id_keyword)
    return render_template('filters.html',
                trademark=trademark, keywords=keywords, keyword_edit=keyword_edit)

@app.route('/logs', methods=['GET'])
def logs():
    '''logs'''
    return render_template('logs.html', twitterlogs=database.get_twitter_logs())

Bootstrap(app)
