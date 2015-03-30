TASK_SELECT = ("t.persistentIdentifier, t.name, t.dateCompleted, "
               "t.blocked, c.name, p.name, t.flagged, t.dateToStart, t.inInbox, t.effectiveInInbox ")


def search_for_task_query(query):
    # Hat tip to markokaestner for this SQL... https://github.com/markokaestner/of-task-actions
    stm_from = ("((task tt left join projectinfo pi on tt.containingprojectinfo=pi.pk) t left join "
                "task p on t.task=p.persistentIdentifier) left join "
                "context c on t.context = c.persistentIdentifier")
    stm_where = ("t.childrenCountAvailable = 0 AND t.blockedByFutureStartDate = 0 "
                 "AND t.dateCompleted IS NULL AND lower(t.name) LIKE lower('%{0}%')".format(query))
    return "SELECT {0} FROM {1} WHERE {2}".format(TASK_SELECT, stm_from, stm_where)


def search_for_inbox_tasks(query):
    stm_from = ("((task tt left join projectinfo pi on tt.containingprojectinfo=pi.pk) t left join "
                "task p on t.task=p.persistentIdentifier) left join "
                "context c on t.context = c.persistentIdentifier")
    stm_where = ("t.effectiveInInbox = 1 OR t.inInbox = 1 "
                 "AND t.dateCompleted IS NULL AND lower(t.name) LIKE lower('%{0}%')".format(query))
    return "SELECT {0} FROM {1} WHERE {2}".format(TASK_SELECT, stm_from, stm_where)
