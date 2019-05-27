# Copyright (C) 2016-2019 ActionTech.
# License: https://www.mozilla.org/en-US/MPL/2.0 MPL version 2 or higher.
import sys
import os
import logging
import json

from steps.step_reload import get_dble_conn

sys.path.append("..")
from behave import *
from hamcrest import *
from lib.DBUtil import *

LOGGER = logging.getLogger('steps.safety')

@Then('Test only schema level permission feature')
def test_schema_permission(context):
    dble_conn = get_dble_conn(context)
    for item in context.table:
        test_conn = DBUtil(context.cfg_dble['dble']['ip'], item['user'], item['password'], item['schema'],
                           context.cfg_dble['client_port'], context)
        sql = "drop table if exists {0}".format(item['table'])
        test_conn.query(sql)
        sql = "create table {0}(id int, data varchar(10))".format(item['table'])
        test_conn.query(sql)
        sql = "insert into {0} values (1,'aaa'),(2,'bbb'),(3,'ccc'),(4,'ddd')".format(item['table'])
        dble_conn.query(sql)
        permission = []
        value = int(item['dml'])
        LOGGER.info("dml: {0}".format(value/1))
        for i in range(4):
            if value%10 == 1:
                if i == 0:
                    permission.append("DELETE")
                if i == 1:
                    permission.append("SELECT")
                if i == 2:
                    permission.append("UPDATE")
                if i == 3:
                    permission.append("INSERT")
            value = value/10
        LOGGER.info("permission: {0}".format(permission))
        del_sql = "delete from {0} where id = 1".format(item['table'])
        sel_sql = "select * from {0}".format(item['table'])
        upd_sql = "update {0} set data='AAA' where id = 1".format(item['table'])
        ins_sql = "insert into {0} values (5, 'eee')".format(item['table'])
        if "DELETE" in permission:
            res, errs = test_conn.query(del_sql)
            assert_that(errs, is_(None))
        else:
            res, errs = test_conn.query(del_sql)
            assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
        if "SELECT" in permission:
            res, errs = test_conn.query(sel_sql)
            assert_that(errs, is_(None))
        else:
            res, errs = test_conn.query(sel_sql)
            assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
        if "UPDATE" in permission:
            res, errs = test_conn.query(upd_sql)
            assert_that(errs, is_(None))
        else:
            res, errs = test_conn.query(upd_sql)
            assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
        if "INSERT" in permission:
            res, errs = test_conn.query(ins_sql)
            assert_that(errs, is_(None))
        else:
            res, errs = test_conn.query(ins_sql)
            assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
        test_conn.close()
    dble_conn.close()

@Then('Test config readonly and schema permission feature')
def test_readonly_schema(context):
    text = json.loads(context.text)
    dble_conn = get_dble_conn(context)
    for item in text:
        test_conn = DBUtil(context.cfg_dble['dble']['ip'], item['user'], item['password'], item['schema'],
                           context.cfg_dble['client_port'], context)
        sql = "drop table if exists {0}".format(item['table'])
        dble_conn.query(sql)
        sql = "create table {0}(id int, data varchar(10))".format(item['table'])
        dble_conn.query(sql)
        sql = "insert into {0} values (1,'aaa'),(2,'bbb'),(3,'ccc'),(4,'ddd')".format(item['table'])
        dble_conn.query(sql)
        permission = []
        value = int(item['dml'])
        LOGGER.info("dml: {0}".format(value / 1))
        for i in range(4):
            if value % 10 == 1:
                if i == 0:
                    permission.append("DELETE")
                if i == 1:
                    permission.append("SELECT")
                if i == 2:
                    permission.append("UPDATE")
                if i == 3:
                    permission.append("INSERT")
            value = value / 10
        LOGGER.info("permission: {0}".format(permission))
        del_sql = "delete from {0} where id = 1".format(item['table'])
        sel_sql = "select * from {0}".format(item['table'])
        upd_sql = "update {0} set data='AAA' where id = 1".format(item['table'])
        ins_sql = "insert into {0} values (5, 'eee')".format(item['table'])
        if "DELETE" in permission:
            res, errs = test_conn.query(del_sql)
            assert_that(errs[1], contains_string('User READ ONLY'))
        if "SELECT" in permission:
            res, errs = test_conn.query(sel_sql)
            assert_that(errs, is_(None))
        else:
            res, errs = test_conn.query(sel_sql)
            assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
        if "UPDATE" in permission:
            res, errs = test_conn.query(upd_sql)
            assert_that(errs[1], contains_string('User READ ONLY'))
        if "INSERT" in permission:
            res, errs = test_conn.query(ins_sql)
            assert_that(errs[1], contains_string('User READ ONLY'))
        test_conn.close()

    dble_conn.close()

@Then('Test config schema and table permission feature')
def test_schema_table(context):
    text = json.loads(context.text)
    dble_conn = get_dble_conn(context)
    for item in text:
        test_conn = DBUtil(context.cfg_dble['dble']['ip'], item['user'], item['password'], item['schema'],
                           context.cfg_dble['client_port'], context)
        sql = "drop table if exists {0}".format(item['single_table'])
        test_conn.query(sql)
        sql = "create table {0}(id int, data varchar(10))".format(item['single_table'])
        test_conn.query(sql)
        sql = "insert into {0} values (1,'aaa'),(2,'bbb'),(3,'ccc'),(4,'ddd')".format(item['single_table'])
        dble_conn.query(sql)
        schema_permission = []
        value = int(item['schema_dml'])
        LOGGER.info("dml: {0}".format(value / 1))
        for i in range(4):
            if value % 10 == 1:
                if i == 0:
                    schema_permission.append("DELETE")
                if i == 1:
                    schema_permission.append("SELECT")
                if i == 2:
                    schema_permission.append("UPDATE")
                if i == 3:
                    schema_permission.append("INSERT")
            value = value / 10
        LOGGER.info("permission: {0}".format(schema_permission))
        del_sql = "delete from {0} where id = 1".format(item['single_table'])
        sel_sql = "select * from {0}".format(item['single_table'])
        upd_sql = "update {0} set data='AAA' where id = 1".format(item['single_table'])
        ins_sql = "insert into {0} values (5, 'eee')".format(item['single_table'])
        if "DELETE" in schema_permission:
            res, errs = test_conn.query(del_sql)
            assert_that(errs, is_(None))
        else:
            res, errs = test_conn.query(del_sql)
            assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
        if "SELECT" in schema_permission:
            res, errs = test_conn.query(sel_sql)
            assert_that(errs, is_(None))
        else:
            res, errs = test_conn.query(sel_sql)
            assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
        if "UPDATE" in schema_permission:
            res, errs = test_conn.query(upd_sql)
            assert_that(errs, is_(None))
        else:
            res, errs = test_conn.query(upd_sql)
            assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
        if "INSERT" in schema_permission:
            res, errs = test_conn.query(ins_sql)
            assert_that(errs, is_(None))
        else:
            res, errs = test_conn.query(ins_sql)
            assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
        for conf_table in item['tables_config']['tables']:
            sql = "drop table if exists {0}".format(conf_table['table'])
            test_conn.query(sql)
            sql = "create table {0}(id int, data varchar(10))".format(conf_table['table'])
            test_conn.query(sql)
            sql = "insert into {0} values (1,'aaa'),(2,'bbb'),(3,'ccc'),(4,'ddd')".format(conf_table['table'])
            dble_conn.query(sql)
            table_permission = []
            value = int(conf_table['dml'])
            for i in range(4):
                if value % 10 == 1:
                    if i == 0:
                        table_permission.append("DELETE")
                    if i == 1:
                        table_permission.append("SELECT")
                    if i == 2:
                        table_permission.append("UPDATE")
                    if i == 3:
                        table_permission.append("INSERT")
                value = value / 10
            del_sql = "delete from {0} where id = 1".format(conf_table['table'])
            sel_sql = "select * from {0}".format(conf_table['table'])
            upd_sql = "update {0} set data='AAA' where id = 1".format(conf_table['table'])
            ins_sql = "insert into {0} values (5, 'eee')".format(conf_table['table'])
            join_sql = "select a.*,b.* from {0} a,{1} b where a.id = b.id".format(item['single_table'], conf_table['table'])
            if "DELETE" in table_permission:
                res, errs = test_conn.query(del_sql)
                assert_that(errs, is_(None))
            else:
                res, errs = test_conn.query(del_sql)
                assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
            if "SELECT" in table_permission:
                res, errs = test_conn.query(sel_sql)
                assert_that(errs, is_(None))
            else:
                res, errs = test_conn.query(sel_sql)
                assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))

            if "SELECT" not in table_permission or "SELECT" not in schema_permission:
                res, errs = test_conn.query(join_sql)
                assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
            else:
                res, errs = test_conn.query(join_sql)
                assert_that(errs, is_(None))
            if "UPDATE" in table_permission:
                res, errs = test_conn.query(upd_sql)
                assert_that(errs, is_(None))
            else:
                res, errs = test_conn.query(upd_sql)
                assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
            if "INSERT" in table_permission:
                res, errs = test_conn.query(ins_sql)
                assert_that(errs, is_(None))
            else:
                res, errs = test_conn.query(ins_sql)
                assert_that(errs[1], contains_string('The statement DML privilege check is not passed'))
            sql = "drop table if exists {0}".format(conf_table['table'])
            test_conn.query(sql)

        test_conn.close()

    dble_conn.close()
