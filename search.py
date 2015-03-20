__author__ = 'Rhyd Lewis'

import sys
from workflow import Workflow, ICON_WEB, web

import sqlite3
import sys
import re
import os

DB_LOCATION = ("/Library/Containers/com.omnigroup.OmniFocus2/"
               "Data/Library/Caches/com.omnigroup.OmniFocus2/OmniFocusDatabase2")
ICON_TASK = "task.png"

log = None

def main(workflow):
    log.debug('Started workflow')

    if len(wf.args):
        query = wf.args[0]
    else:
        query = None

    log.debug('Query: {0}'.format(query))

    from os.path import expanduser
    home = expanduser("~")

    db_path = "{0}/{1}".format(home, DB_LOCATION)
    if not os.path.isfile(db_path):
        db_path = re.sub(".OmniFocus2", ".OmniFocus2.MacAppStore", db_path)
    log.debug(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    stm_select = "t.persistentIdentifier, t.name, t.dateCompleted, c.name, p.name"
    stm_from = ("((task tt left join projectinfo pi on tt.containingprojectinfo=pi.pk) t left join "
                "task p on t.task=p.persistentIdentifier) left join context c on t.context = c.persistentIdentifier")
    stm_where = ("t.blocked = 0 AND t.childrenCountAvailable = 0 AND t.blockedByFutureStartDate = 0 "
                 "AND t.dateCompleted IS NULL AND lower(t.name) LIKE lower('%{0}%')".format(query))
    sql = "SELECT {0} FROM {1} WHERE {2}".format(stm_select, stm_from, stm_where)

    log.debug(sql)

    c.execute(sql)
    rows = c.fetchall()

    log.debug(len(rows))

    for row in rows:
        ofid = row[0]
        name = row[1]
        project = row[4]
        log.debug("Found Task {0}, '{1}' from project '{2}'".format(ofid, name, project))
        workflow.add_item(title=name, subtitle=project, icon=ICON_TASK, arg=ofid, valid=True)

    wf.send_feedback()

if __name__ == u"__main__":
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))