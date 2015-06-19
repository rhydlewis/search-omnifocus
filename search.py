from __future__ import unicode_literals

import sqlite3
import sys
import re
import os
import argparse

from workflow import Workflow
import factory
import queries

DB_LOCATION = ("/Library/Containers/com.omnigroup.OmniFocus2/"
               "Data/Library/Caches/com.omnigroup.OmniFocus2/OmniFocusDatabase2")
TASK = "t"
PROJECT = "p"
CONTEXT = "c"
log = None


def main(wf):
    log.debug('Started workflow')
    args = parse_args()

    if args.type == PROJECT:
        log.debug('Searching for projects...')
        sql = queries.search_for_projects(args)
    else:
        log.debug('Searching for tasks...')
        sql = queries.search_for_tasks(args)

    for result in run_query(sql):
        log.debug(result)
        if args.type == PROJECT:
            item = factory.create_project(result)
        else:
            item = factory.create_task(result)
        log.debug(item)
        wf.add_item(title=item.name, subtitle=item.subtitle, icon=item.icon, arg=item.persistent_id, valid=True)

    wf.send_feedback()


def parse_args():
    # python search.py -t <task|project|context> -a Active tasks -i Inbox only
    parser = argparse.ArgumentParser(description="Search OmniFocus")
    # add query type parameter?
    parser.add_argument('-i', '--inbox-only', action='store_true', help='search OmniFocus inbox only')
    parser.add_argument('-a', '--active-only', action='store_true', help='search for active tasks only')
    parser.add_argument('-t', '--type', default=TASK, choices=[TASK, PROJECT], type=str,
                        help='What to search for ((t)ask, (p)roject or (c)ontext)?')
    parser.add_argument('query', type=unicode, nargs=argparse.REMAINDER, help='query string')

    log.debug(wf.args)
    args = parser.parse_args(wf.args)
    return args


def find_omnifocus():
    home = os.path.expanduser("~")
    location = "{0}/{1}".format(home, DB_LOCATION)
    if not os.path.isfile(location):
        location = re.sub(".OmniFocus2", ".OmniFocus2.MacAppStore", location)

    log.debug(location)

    return location


def run_query(sql):
    conn = sqlite3.connect(find_omnifocus())
    c = conn.cursor()
    log.debug(sql)
    c.execute(sql)
    results = c.fetchall()
    log.debug("Found {0} results".format(len(results)))
    c.close()
    return results


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
