from __future__ import unicode_literals

TASK_SELECT = ("t.persistentIdentifier, t.name, t.dateCompleted, "
               "t.blocked, c.name, p.name, t.flagged, t.dateToStart, "
               "t.inInbox, t.effectiveInInbox, t.effectiveDateToStart ")
TASK_FROM = ("((task tt left join projectinfo pi on tt.containingprojectinfo=pi.pk) t left join "
             "task p on t.task=p.persistentIdentifier) left join "
             "context c on t.context = c.persistentIdentifier")
TASK_NAME_WHERE = "lower(t.name) LIKE lower('%{0}%')"


def search_for_tasks(args):
    query = args.query
    if len(query) == 0 and args.inbox_only:
        sql = all_inbox_tasks()
    elif args.inbox_only:
        sql = search_inbox_tasks(query[0])
    else:
        sql = search_all_tasks(args.active_only, query[0])

    return sql

def search_for_projects(args):
    sql = search_projects(args.query[0])
    return sql


def search_all_tasks(active_only, query):
    # Hat tip to markokaestner for this SQL... https://github.com/markokaestner/of-task-actions

    # stm_where = ("t.childrenCountAvailable = 0 AND t.blockedByFutureStartDate = 0 AND "
    stm_where = ("t.childrenCountAvailable = 0 AND "
                 "(t.effectiveInInbox = 0 AND t.inInbox = 0) AND "
                 "t.dateCompleted IS NULL AND ")
    stm_where = (stm_where + TASK_NAME_WHERE).format(query)

    if active_only:
        stm_where = ("t.blocked = 0 AND " + stm_where)

    return "SELECT {0} FROM {1} WHERE {2}".format(TASK_SELECT, TASK_FROM, stm_where)


def search_inbox_tasks(query):
    stm_where = ("(t.effectiveInInbox = 1 OR t.inInbox = 1) AND "
                 "t.dateCompleted IS NULL AND ")
    stm_where = (stm_where + TASK_NAME_WHERE).format(query)
    return "SELECT {0} FROM {1} WHERE {2}".format(TASK_SELECT, TASK_FROM, stm_where)


def all_inbox_tasks():
    stm_where = "(t.effectiveInInbox = 1 OR t.inInbox = 1) AND t.dateCompleted IS NULL"
    return "SELECT {0} FROM {1} WHERE {2}".format(TASK_SELECT, TASK_FROM, stm_where)


def search_projects(query):
    stm_select = ("p.pk, t.name, p.status, p.numberOfAvailableTasks, "
                  "p.numberOfRemainingTasks, p.containsSingletonActions, f.name, t.dateToStart, t.effectiveDateToStart")
    stm_from = ("(ProjectInfo p LEFT JOIN Task t ON p.task=t.persistentIdentifier) "
                "LEFT JOIN Folder f ON p.folder=f.persistentIdentifier")
    # removed p.status = 'active' AND
    stm_where = "lower(t.name) LIKE lower('%{0}%')".format(query)
    stm_order = "p.containsSingletonActions DESC, t.name ASC"

    return "SELECT {0} FROM {1} WHERE {2} ORDER BY {3}".format(stm_select, stm_from, stm_where, stm_order)