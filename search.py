from __future__ import unicode_literals

import sqlite3
import sys
import re
import os
import argparse
import datetime

from workflow import Workflow, ICON_WARNING
import factory
import queries
import omnifocus

DB_KEY = 'db_path'
DB_LOCATION = ("/Library/Containers/com.omnigroup.OmniFocus2/"
               "Data/Library/Caches/com.omnigroup.OmniFocus2/OmniFocusDatabase2")
MAS_DB_LOCATION = re.sub('.OmniFocus2', '.OmniFocus2.MacAppStore', DB_LOCATION)

TASK = "t"
INBOX = "i"
PROJECT = "p"
CONTEXT = "c"
PERSPECTIVE = "v"
FOLDER = "f"
log = None

SINGLE_QUOTE = "'"
ESC_SINGLE_QUOTE = "''"


def main(wf):
    log.debug('Started workflow')
    args = parse_args()

    if args.type != PERSPECTIVE:
        sql = populate_query(args)
        get_results(sql, args.type)
    else:
        get_perspectives(args)

    workflow.send_feedback()


def get_results(sql, query_type):
    results = run_query(sql)

    if not results:
        workflow.add_item('No items', icon=ICON_WARNING)
    else:
        for result in results:
            log.debug(result)
            if query_type == PROJECT:
                item = factory.create_project(result)
            elif query_type == CONTEXT:
                item = factory.create_context(result)
            elif query_type == FOLDER:
                item = factory.create_folder(result)
            else:
                item = factory.create_task(result)
            log.debug(item)
            workflow.add_item(title=item.name, subtitle=item.subtitle, icon=item.icon,
                              arg=item.persistent_id, valid=True)


def get_perspectives(args):
    if args.query:
        query = args.query[0]
        log.debug("Searching perspectives for '{0}'".format(query))
        perspectives = omnifocus.search_perspectives(query)
    else:
        log.debug("Finding all perspectives")
        perspectives = omnifocus.list_perspectives()

    if not perspectives:
        workflow.add_item('No items', icon=ICON_WARNING)
    else:
        for perspective in perspectives:
            log.debug(perspective)
            item = factory.create_perspective(perspective)
            log.debug(item)
            workflow.add_item(title=item.name, subtitle=item.subtitle, icon=item.icon,
                              arg=item.name,
                              valid=True)


def populate_query(args):
    query = None
    if args.query:
        query = args.query[0]

        if SINGLE_QUOTE in query:
            query = re.sub(SINGLE_QUOTE, ESC_SINGLE_QUOTE, query)

    active_only = args.active_only
    if args.type == PROJECT:
        log.debug('Searching projects')
        sql = queries.search_projects(active_only, query)
    elif args.type == CONTEXT:
        log.debug('Searching contexts')
        sql = queries.search_contexts(query)
    elif args.type == FOLDER:
        log.debug('Searching folder')
        sql = queries.search_folders(query)
    elif args.type == INBOX:
        log.debug('Searching inbox')
        sql = queries.search_inbox(query)
    else:
        log.debug('Searching tasks')
        sql = queries.search_tasks(active_only, query)
    return sql


def parse_args():
    parser = argparse.ArgumentParser(description="Search OmniFocus")
    parser.add_argument('-a', '--active-only', action='store_true',
                        help='search for active tasks only')
    parser.add_argument('-t', '--type', default=TASK,
                        choices=[INBOX, TASK, PROJECT, CONTEXT, PERSPECTIVE, FOLDER], type=str,
                        help='What to search for: (b)oth tasks and projects, (t)ask, (p)roject, '
                             '(c)ontext, (f)older or perspecti(v)e?')
    parser.add_argument('query', type=unicode, nargs=argparse.REMAINDER, help='query string')

    log.debug(workflow.args)
    args = parser.parse_args(workflow.args)
    return args


def find_omnifocus():
    home = os.path.expanduser("~")
    db = "{0}{1}".format(home, DB_LOCATION)
    mas = "{0}{1}".format(home, MAS_DB_LOCATION)

    if not os.path.isfile(db):
        log.debug("Omnifocus db not found at {0}; using {1} instead".format(db, mas))
        db = mas
    elif os.path.isfile(mas):
        db_mod = mod_date(db)
        mas_mod = mod_date(mas)
        if db_mod < mas_mod:
            db = mas
        log.debug("Omnifocus direct and MAS db's found; using {0} as it's newer "
                  "(Direct {1} vs. MAS {2})".format(db, db_mod, mas_mod))

    log.debug(db)
    return db


def mod_date(filename):
    mtime = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(mtime)


def run_query(sql):
    db_path = workflow.stored_data(DB_KEY)
    if not db_path:
        db_path = find_omnifocus()
        workflow.store_data(DB_KEY, db_path)
    else:
        log.debug(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    log.debug(sql)
    cursor.execute(sql)
    results = cursor.fetchall()
    log.debug("Found {0} results".format(len(results)))
    cursor.close()
    return results


if __name__ == '__main__':
    workflow = Workflow()
    log = workflow.logger
    sys.exit(workflow.run(main))
