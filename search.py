from __future__ import unicode_literals

import sqlite3
import sys
import os
import argparse
import datetime

from workflow import Workflow, ICON_WARNING, ICON_SYNC

from factory import Factory
from omnifocus import DEFAULT_OF_VERSION
import queries
import omnifocus

DB_KEY = 'db_path'
VERSION_KEY = 'of_version'
ICON_ROOT = 'icon_path'
OF2_DB_LOCATION = "/Library/Containers/com.omnigroup.OmniFocus2/Data/Library/Caches/com.omnigroup.OmniFocus2/OmniFocusDatabase2"
OF2_MAS_DB_LOCATION = OF2_DB_LOCATION.replace('.OmniFocus2', '.OmniFocus2.MacAppStore')
OF3_DB_LOCATION = "/Library/Containers/com.omnigroup.OmniFocus3/Data/Library/Application Support/OmniFocus/OmniFocus Caches/OmniFocusDatabase"
OF3_MAS_DB_LOCATION = OF3_DB_LOCATION.replace('.OmniFocus3', '.OmniFocus3.MacAppStore')

OF_ICON_ROOT = '/Applications/OmniFocus.app/Contents/Resources'

# Update workflow from GitHub repo
UPDATE_SETTINGS = {'github_slug': 'rhydlewis/search-omnifocus'}
SHOW_UPDATES = True

TASK = "t"
INBOX = "i"
PROJECT = "p"
CONTEXT = "c"
PERSPECTIVE = "v"
FOLDER = "f"
FLAGGED = "g"
NOTES = "n"
RECENT = "r"
DUE = "d"
VERSION_SWITCH = "s"
log = None

SINGLE_QUOTE = "'"
ESC_SINGLE_QUOTE = "''"


def main(wf):
    log.debug('Started workflow')
    args = parse_args()

    if SHOW_UPDATES and workflow.update_available:
        wf.add_item('A new version is available', 'Action this item to install the update',
                    autocomplete='workflow:update', icon=ICON_SYNC)

    set_omnifocus_version(args)
    omnifocus_version = wf.settings[VERSION_KEY]
    log.info("Using OmniFocus version {0}".format(omnifocus_version))

    factory = Factory(find_omnifocus_icons(), omnifocus_version)

    if args.type != PERSPECTIVE:
        sql = populate_query(args)
        get_results(sql, args.type, factory)
    else:
        get_perspectives(args, factory)

    wf.send_feedback()

def set_omnifocus_version(args):
    set_version = args.switch_versions
    if set_version:
        workflow.settings[VERSION_KEY] = set_version
        print('Now using OmniFocus v{0} for search results'.format(set_version))
        exit(1)
    elif not workflow.settings.has_key(VERSION_KEY):
        workflow.settings[VERSION_KEY] = DEFAULT_OF_VERSION


def get_results(sql, query_type, factory):
    workflow.logger.debug(sql)
    results = run_query(sql)

    if not results:
        workflow.add_item('No items', icon=ICON_WARNING)
    else:
        for result in results:
            if query_type == PROJECT:
                item = factory.create_project(result)
            elif query_type == CONTEXT:
                item = factory.create_context(result)
            elif query_type == FOLDER:
                item = factory.create_folder(result)
            elif query_type == RECENT:
                item = factory.create_recent_item(result)
            else:
                item = factory.create_task(result)
            log.debug(item)
            workflow.add_item(title=item.name, subtitle=item.subtitle, icon=item.icon,
                              arg=item.persistent_id, valid=True)


def get_perspectives(args, factory):
    version = workflow.settings[VERSION_KEY]

    if args.query:
        query = args.query[0]
        log.debug("Searching perspectives for '{0}'".format(query))
        perspectives = omnifocus.search_perspectives(query, version)
    else:
        log.debug("Finding all perspectives")
        perspectives = omnifocus.list_perspectives(version)

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
            query = query.replace(SINGLE_QUOTE, ESC_SINGLE_QUOTE)

    active_only = args.active_only
    flagged_only = args.flagged_only
    everything = args.everything

    if args.type == PROJECT:
        log.debug('Searching projects')
        sql = queries.search_projects(active_only, query)
    elif args.type == CONTEXT:
        log.debug('Searching contexts/tags')
        sql = queries.search_tags(query)
    elif args.type == FOLDER:
        log.debug('Searching folder')
        sql = queries.search_folders(query)
    elif args.type == INBOX:
        log.debug('Searching inbox')
        sql = queries.search_inbox(query)
    elif args.type == NOTES:
        log.debug('Searching inbox')
        sql = queries.search_notes(active_only, flagged_only, query)
    elif args.type == RECENT:
        log.debug('Searching recent items')
        sql = queries.show_recent_tasks(active_only)
    elif args.due:
        log.debug('Listing overdue or due items')
        sql = queries.show_due_tasks(workflow.settings[VERSION_KEY])
    else:
        log.debug('Searching tasks')
        sql = queries.search_tasks(active_only, flagged_only, query, everything)
    return sql


def parse_args():
    parser = argparse.ArgumentParser(description="Search OmniFocus")
    parser.add_argument('-a', '--active-only', action='store_true', help='search for active tasks only')
    parser.add_argument('-g', '--flagged-only', action='store_true', help='search for flagged tasks only')
    parser.add_argument('-e', '--everything', action='store_true',
                        help='search for tasks in the inbox as well as processed tasks')
    parser.add_argument('-t', '--type', default=TASK,
                        choices=[INBOX, TASK, PROJECT, CONTEXT, PERSPECTIVE, FOLDER, NOTES, RECENT],
                        type=str, help='What to search for: (b)oth tasks and projects, (t)ask, '
                                       '(p)roject, (c)ontext, (f)older, perspecti(v)e, '
                                       'task (n)otes or (r)ecent items?')
    parser.add_argument('-d', '--due', action='store_true', help='show overdue or due items')
    parser.add_argument('-s', '--switch-versions', choices=["2", "3"])
    parser.add_argument('query', type=unicode, nargs=argparse.REMAINDER, help='query string')

    log.debug(workflow.args)
    args = parser.parse_args(workflow.args)
    return args


def find_omnifocus_icons():
    if not workflow.settings.has_key(ICON_ROOT):
        icon_root = OF_ICON_ROOT
        if not os.path.isdir(icon_root):
            icon_root = omnifocus.find_install_location() + "Contents/Resources"
        workflow.settings[ICON_ROOT] = icon_root
        log.debug("Storing icon_root as '{0}'".format(icon_root))
    else:
        icon_root = workflow.settings[ICON_ROOT]
        log.debug("Using stored icon_root:'{0}'".format(icon_root))

    return icon_root


def find_omnifocus_db():
    if workflow.settings[VERSION_KEY] == DEFAULT_OF_VERSION:
        non_mas_location = OF3_DB_LOCATION
        mas_location = OF3_MAS_DB_LOCATION
    else:
        non_mas_location = OF2_DB_LOCATION
        mas_location = OF2_MAS_DB_LOCATION

    home = os.path.expanduser("~")
    db = "{0}{1}".format(home, non_mas_location)
    mas = "{0}{1}".format(home, mas_location)

    if not os.path.isfile(db):
        log.debug("OmniFocus db not found at {0}; using {1} instead".format(db, mas))
        db = mas
    elif os.path.isfile(mas):
        db_mod = mod_date(db)
        mas_mod = mod_date(mas)
        if db_mod < mas_mod:
            db = mas
        log.debug("OmniFocus direct and MAS db's found; using {0} as it's newer "
                  "(Direct {1} vs. MAS {2})".format(db, db_mod, mas_mod))

    log.debug(db)
    return db


def mod_date(filename):
    mtime = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(mtime)


def run_query(sql):
    db_path = find_omnifocus_db()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    log.debug(sql)
    cursor.execute(sql)
    results = cursor.fetchall()
    log.debug("Found {0} results".format(len(results)))
    cursor.close()
    return results


if __name__ == '__main__':
    workflow = Workflow(update_settings=UPDATE_SETTINGS)
    log = workflow.logger
    sys.exit(workflow.run(main))
