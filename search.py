__author__ = 'Rhyd Lewis'

import sqlite3
import sys
import re
import os

from workflow import Workflow, ICON_INFO
from task import Task

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

    # Hat tip to markokaestner for this SQL... https://github.com/markokaestner/of-task-actions
    stm_select = "t.persistentIdentifier, t.name, t.dateCompleted, t.blocked, c.name, p.name, t.flagged, t.dateToStart "
    stm_from = ("((task tt left join projectinfo pi on tt.containingprojectinfo=pi.pk) t left join "
                "task p on t.task=p.persistentIdentifier) left join context c on t.context = c.persistentIdentifier")
    # stm_where = ("t.blocked = 0 AND t.childrenCountAvailable = 0 AND t.blockedByFutureStartDate = 0 "
    stm_where = ("t.childrenCountAvailable = 0 AND t.blockedByFutureStartDate = 0 "
                 "AND t.dateCompleted IS NULL AND lower(t.name) LIKE lower('%{0}%')".format(query))
    sql = "SELECT {0} FROM {1} WHERE {2}".format(stm_select, stm_from, stm_where)

    log.debug(sql)

    c.execute(sql)
    rows = c.fetchall()

    log.debug("Found {0} results".format(len(rows)))

    for row in rows:
        t = create_task(row)
        # log.debug(str(t))

        icon = ICON_TASK

        if t.is_blocked == 1:
            icon = ICON_INFO

        workflow.add_item(title=t.name, subtitle=t.project, icon=icon, arg=t.persistent_id, valid=True)

    wf.send_feedback()


def create_task(row):
    log.debug(row)
    n = row[1]#.encode('utf8', 'ignore')
    p = row[5]#.encode('utf8', 'ignore')
    return Task(persistent_id=row[0], name=n, is_complete=row[2], is_blocked=row[3], context=row[4],
                project=p)


if __name__ == u"__main__":
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))