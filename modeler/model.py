#!/bin/python
# -*- coding: utf-8 -*-
# @File  : model.py
# @Author: wangms
# @Date  : 2019/6/24
# @Brief: 简述报表功能
from app import db
from datetime import datetime


class DBInfo(db.Model):
    __tablename__ = "t_db_info"
    db_id = db.Column("db_id", db.Integer, autoincrement=True, primary_key=True)
    db_host = db.Column("db_host", db.String)
    db_port = db.Column("db_port", db.String)
    db_name = db.Column("db_name", db.String)
    db_short_name = db.Column("db_short_name", db.String, unique=True)
    db_user = db.Column("db_user", db.String)
    db_password = db.Column("db_password", db.String)
    creation_time = db.Column("creation_time", db.DateTime, default=datetime.now())
    status = db.Column("status", db.Integer, default=0)

    tables = db.relationship('TableInfo', backref='db', lazy=True)


class TableInfo(db.Model):
    __tablename__ = "t_table_info"
    table_id = db.Column("table_id", db.Integer, autoincrement=True, primary_key=True)
    schema_name = db.Column("schema_name", db.String)
    table_name = db.Column("table_name", db.String)
    table_owner = db.Column("table_owner", db.String)
    total_count = db.Column("total_count", db.Integer)
    pos_x = db.Column("pos_x", db.Float)
    pos_y = db.Column("pos_y", db.Float)
    db_id = db.Column("db_id", db.ForeignKey('t_db_info.db_id'), nullable=False)

    columns = db.relationship('ColumnInfo', backref='table', lazy=True)


class ColumnInfo(db.Model):
    __tablename__ = 't_columns_info'
    column_id = db.Column("column_id", db.Integer, autoincrement=True, primary_key=True)
    column_name = db.Column("column_name", db.String)
    data_type = db.Column("data_type", db.String)
    is_not_null = db.Column("is_not_null", db.Boolean)
    column_num = db.Column("column_num", db.Integer)
    table_id = db.Column("table_id", db.ForeignKey('t_table_info.table_id'), nullable=False)


ColumnRelation = db.Table('t_column_relation',
    db.Column('source_column_id', db.Integer, db.ForeignKey('t_columns_info.column_id'), primary_key=True),
    db.Column('target_column_id', db.Integer, db.ForeignKey('t_columns_info.column_id'), primary_key=True),
    db.Column('relation', db.String)
)





