#!/bin/python
# -*- coding: utf-8 -*-
# @File  : service.py
# @Author: wangms
# @Date  : 2019/6/24
# @Brief: 简述报表功能
from common.utils import DBConnect, Result


class ModelerService(object):
    @classmethod
    def search_all_schema(cls, db_short_name):
        try:
            with DBConnect(db_short_name) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT DISTINCT n.nspname as schema_name
                        FROM pg_catalog.pg_class c,
                             pg_catalog.pg_namespace n
                        WHERE pg_catalog.pg_table_is_visible(c.oid)
                          AND n.oid=c.relnamespace
                          AND c.relkind in ('r','p')
                          AND c.relispartition=false
                        ORDER BY 1;
                    """)
                    all_schemas = cursor.fetchall()
        except Exception as e:
            return Result(False, str(e))
        return Result(True, all_schemas)

    @classmethod
    def search_all_tables_info(cls, db_short_name, schema_name):
        try:
            with DBConnect(db_short_name) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT c.oid,
                               n.nspname as schema_name,
                               c.relname as table_name,
                               u.usename as table_owner
                        FROM pg_catalog.pg_class c
                        LEFT JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
                        LEFT JOIN pg_catalog.pg_user u ON u.usesysid=c.relowner
                        WHERE pg_catalog.pg_table_is_visible(c.oid)
                          AND n.nspname='{}'
                          AND c.relkind in ('r','p')
                          AND c.relispartition=false
                        ORDER BY 2, 3;
                    """.format(schema_name))
                    all_tables = cursor.fetchall()
        except Exception as e:
            return Result(False, str(e))
        return Result(True, all_tables)

    @classmethod
    def search_column_by_oid(cls, db_short_name, oid):
        all_columns = []
        try:
            with DBConnect(db_short_name) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT a.attname                                        AS column_name,
                               pg_catalog.format_type(a.atttypid,a.atttypmod)   AS data_type, 
                               pg_catalog.col_description(a.attrelid, a.attnum) AS description,
                               a.attnum                                         AS column_num,
                               a.attnotnull                                     AS is_not_null
                        FROM pg_catalog.pg_attribute a
                        WHERE a.attrelid = {} 
                          AND a.attnum > 0 
                          AND NOT a.attisdropped
                        ORDER BY a.attnum
                    """.format(oid))
                    for column_name, data_type, description, column_num, not_null in cursor.fetchall():
                        all_columns.append((
                            column_name, data_type, description, column_num, not_null
                        ))
        except Exception as e:
            return Result(False, str(e))
        return Result(True, all_columns)

    @classmethod
    def fetch_tables_from_db(cls, db_short_name):
        try:
            with DBConnect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        select table_id,schema_name,table_name,
                               table_owner,total_count,pos_x,pos_y,a.db_id
                        from t_table_info a, 
                             t_db_info b
                        where a.db_id=b.db_id
                          and b.db_short_name=%s
                        order by schema_name, table_name
                    """, (db_short_name,))

                    tables = cursor.fetchall()
        except Exception as e:
            return Result(False, str(e))
        return Result(True, tables)

    @classmethod
    def fetch_columns_from_db(cls, table_id):
        try:
            with DBConnect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        select column_name,data_type,description
                        from t_columns_info a
                        where table_id=%s
                        order by column_num
                    """, (table_id,))

                    columns = cursor.fetchall()
        except Exception as e:
            return Result(False, str(e))
        return Result(True, columns)

    @classmethod
    def fetch_relations_from_db(cls, source_table_id):
        relations = {}
        try:
            with DBConnect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        select a.source_table_id,
                               d.schema_name||'.'||d.table_name as source_table_name,
                               a.source_column_names,
                               a.target_table_id,
                               e.schema_name||'.'||e.table_name as target_table_name,
                               a.target_column_names,
                               a.relation_id
                        from t_column_relation a,
                             t_table_info   d,
                             t_table_info   e
                        where a.source_table_id=d.table_id
                          and a.target_table_id=e.table_id
                          and a.source_table_id=%s
                        order by a.source_table_id,a.target_table_id
                    """, (source_table_id,))
                    for i in cursor.fetchall():
                        key = "{}-{}".format(i.source_table_id, i.target_table_id)
                        relations[key] = [
                            i.source_table_name, i.source_column_names.split(','),
                            i.target_table_name, i.target_column_names.split(','), i.relation_id]

        except Exception as e:
            return Result(False, str(e))
        return Result(True, relations)

    @classmethod
    def save_table_column(cls, db_short_name, table_info, columns_info):
        try:
            with DBConnect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        select db_id
                        from t_db_info 
                        where db_short_name=%s
                    """, (db_short_name,))

                    db_id = cursor.fetchone()[0]

                    cursor.execute("""
                        insert into t_table_info(schema_name, table_name, table_owner, db_id)
                        values (%s, %s, %s, %s)
                    """, (table_info[0], table_info[1], table_info[2], db_id,))
                    conn.commit()

                    cursor.execute("""
                        select table_id from t_table_info
                        where schema_name=%s and table_name=%s
                    """, (table_info[0], table_info[1],))
                    table_id = cursor.fetchone()[0]

                    for column in columns_info:
                        cursor.execute("""
                            insert into t_columns_info(column_name, data_type, description, column_num, is_not_null, table_id)
                            values (%s, %s, %s, %s, %s, %s)
                        """, (column[0], column[1], column[2], column[3], column[4], table_id,))
                    conn.commit()

        except Exception as e:
            return Result(False, str(e))
        return Result(False, 200)

    @classmethod
    def drop_table_column(cls, table_name):
        table = table_name.split('.')
        try:
            with DBConnect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        select table_id from t_table_info
                        where schema_name=%s and table_name=%s
                    """, (table[0], table[1],))

                    table_id = cursor.fetchone()[0]

                    cursor.execute("""
                        delete from t_column_relation
                        where source_table_id=%s or target_table_id=%s
                    """, (table_id, table_id,))
                    conn.commit()

                    cursor.execute("""
                        delete from t_columns_info where table_id=%s
                    """, (table_id,))
                    conn.commit()

                    cursor.execute("""
                        delete from t_table_info where table_id=%s
                    """, (table_id,))
                    conn.commit()

        except Exception as e:
            return Result(False, str(e))
        return Result(False, 200)

    @classmethod
    def save_table_position(cls, db_short_name, table_info):
        tb_info = [{
            'schema': tb.split('.')[0],
            'table': tb.split('.')[1],
            'pos_x': float(pos.split(',')[0]),
            'pos_y': float(pos.split(',')[1])
        } for tb, pos in table_info.items()]

        try:
            with DBConnect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                            SELECT db_id
                            FROM t_db_info 
                            WHERE db_short_name=%s
                        """, (db_short_name,))

                    db_id = cursor.fetchone()[0]

                    for tb in tb_info:
                        cursor.execute("""
                                UPDATE t_table_info
                                SET pos_x=%s, pos_y=%s
                                WHERE db_id=%s AND table_name=%s AND schema_name=%s
                            """, (tb['pos_x'], tb['pos_y'], db_id, tb['table'], tb['schema'],))
                        conn.commit()

        except Exception as e:
            return Result(False, str(e))
        return Result(False, 200)

    @classmethod
    def save_column_relation(cls, source_table, source_columns, target_table, target_columns, relation):
        source_table = source_table.split('.')
        target_table = target_table.split('.')
        try:
            with DBConnect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        select table_id from t_table_info
                        where schema_name=%s and table_name=%s
                    """, (source_table[0], source_table[1],))
                    source_table_id = cursor.fetchone()[0]

                    cursor.execute("""
                        select table_id from t_table_info
                        where schema_name=%s and table_name=%s
                    """, (target_table[0], target_table[1],))
                    target_table_id = cursor.fetchone()[0]

                    cursor.execute("""
                        delete from t_column_relation
                        where source_table_id=%s and target_table_id=%s
                    """, (source_table_id, target_table_id))
                    conn.commit()

                    if source_columns == [] or target_columns == []:
                        pass
                    else:
                        source_column_names = ''
                        target_column_names = ''
                        for src in source_columns:
                            source_column_names = source_column_names + src + ','
                        for tat in target_columns:
                            target_column_names = target_column_names + tat + ','

                        source_column_names = source_column_names[:len(source_column_names) - 1]
                        target_column_names = target_column_names[:len(target_column_names) - 1]

                        cursor.execute("""
                            insert into t_column_relation(source_table_id, source_column_names, 
                            target_table_id, target_column_names, relation_id)
                            values (%s, %s, %s, %s, %s)
                        """, (source_table_id, source_column_names, target_table_id, target_column_names, relation))
                        conn.commit()

        except Exception as e:
            return Result(False, str(e))
        return Result(False, 200)


