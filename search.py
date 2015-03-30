import sqlite3
import sys
import re
import os

from workflow import Workflow, ICON_INFO
import taskfactory
import queries

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

    sql = queries.search_for_task_query(query)

    log.debug(sql)

    c.execute(sql)
    rows = c.fetchall()

    log.debug("Found {0} results".format(len(rows)))

    for row in rows:
        log.debug(row)
        t = taskfactory.create_task(row)
        workflow.add_item(title=t.name, subtitle=t.project, icon=t.icon, arg=t.persistent_id, valid=True)

    wf.send_feedback()

if __name__ == u"__main__":
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))