#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2019/6/24
# @Brief: 简述报表功能
from modeler import modeler
from flask import request, jsonify, session, \
    Response, render_template, url_for, redirect
import json
from modeler.service import ModelerService


@modeler.route("/modeler", methods=["GET"])
def index():
    if not session.get("username"):
        return redirect(url_for("admin.login", callback=request.url))
    db_short_name = request.args.get("dbShortName")
    session["db_short_name"] = db_short_name
    result = ModelerService.search_all_schema(db_short_name)
    if not result.status:
        return Response(result.content, status=403)
    return render_template("konva_modeler.html", schemas=result.content)


@modeler.route("/modeler/model", methods=["GET"])
def fetch_model():
    result = ModelerService.fetch_tables_from_db(session["db_short_name"])
    if not result.status:
        return Response(result.content, status=403)
    all_tables = []
    tables = result.content
    for t in tables:
        result = ModelerService.fetch_columns_from_db(t.table_id)
        if not result.status:
            return Response(result.content, status=403)

        all_tables.append({
            "table_id": t.table_id,
            "schema_name": t.schema_name,
            "table_name": t.table_name,
            "table_owner": t.table_owner,
            "total_count": t.total_count,
            "pos_x": t.pos_x,
            "pos_y": t.pos_y,
            "db_id": t.db_id,
            "columns": result.content,
        })
    relations = []
    for t in tables:
        result = ModelerService.fetch_relations_from_db(t.table_id)
        if not result.status:
            return Response(result.content, status=403)
        relations += list(result.content.values())

    return Response(json.dumps({
        "all_tables": all_tables,
        "relations": relations
    }), mimetype="application/json")


@modeler.route("/modeler/tables", methods=["GET", "POST"])
def fetch_tables():
    db_short_name = session["db_short_name"]
    schema = request.form.get("schema")
    result = ModelerService.search_all_tables_info(db_short_name, schema)
    session["table_info"] = result.content
    if not result.status:
        return Response(result.content, status=403)
    table = [table.table_name for table in result.content]
    return jsonify({"table": table})


@modeler.route("/modeler/model/add", methods=["GET", "POST"])
def add_model():
    schema_name = request.form.get("schema")
    table_name = request.form.get("table")
    try:
        oid, schema, table, user = tuple(filter(lambda x: x[2] == table_name, session["table_info"]))[0]
        result = ModelerService.search_column_by_oid(session["db_short_name"], oid)
        session[schema_name + '.' + table_name] = result.content
        column_info = [column[0:3] for column in result.content]
        ModelerService.save_table_column(session["db_short_name"], (schema, table, user), result.content)
    except Exception as e:
        return Response(str(e), status=403)


    return jsonify({
        'table': table_name,
        'columns': column_info
    })


@modeler.route("/modeler/model/drop", methods=["POST"])
def drop_model():
    table_name = request.form.get("table_name")
    ModelerService.drop_table_column(table_name)

    return Response(status=200)


@modeler.route("/modeler/save/position", methods=["POST"])
def save_position():
    db_short_name = session["db_short_name"]
    table_info = json.loads(request.form.get("table_info"))
    ModelerService.save_table_position(db_short_name, table_info)

    return Response(status=200)


@modeler.route("/modeler/relation/add", methods=["POST"])
def save_relation():
    source_table = request.form.get("source_table")
    source_columns = json.loads(request.form.get("source_columns"))
    target_table = request.form.get("target_table")
    target_columns = json.loads(request.form.get("target_columns"))
    relation = request.form.get("relation")
    ModelerService.save_column_relation(source_table, source_columns, target_table, target_columns, relation)

    return Response(status=200)
