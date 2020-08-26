from __future__ import unicode_literals

from omnifocus import DEFAULT_OF_VERSION

ID = str("id")
NAME = str("name")
BLOCKED_BY_START_DATE = str("blocked_by_future_start_date")
PROJECT_NAME = str("project_name")
START_DATE = str("start_date")
IN_INBOX = str("in_inbox")
EFFECTIVE_IN_INBOX = str("effective_in_inbox")
EFFECTIVE_START_DATE = str("effective_start_date")
CHILD_COUNT = str("child_count")
BLOCKED = str("blocked")
STATUS = str("status")
DUE_DATE = str("due_date")
AVAILABLE_TASK_COUNT = str("available_task_count")
REMAINING_TASK_COUNT = str("remaining_task_count")
SINGLETON = str("singleton")
FOLDER_NAME = str("folder_name")
ALLOWS_NEXT_ACTION = str("allows_next_action")
CONTAINING_PROJECT_INFO = str("parent")
MODIFIED_DATE = str("modified")
PROJECT_IS_REMAINING = str("project_remaining")


NAME_SORT = "name ASC"
TASK_SELECT = ", ".join([
    "t.persistentIdentifier AS {0}".format(ID),
    "t.name AS {0}".format(NAME),
    "t.dateCompleted",
    "t.blockedByFutureStartDate AS {0}".format(BLOCKED_BY_START_DATE),
    "p.name AS {0}".format(PROJECT_NAME),
    "t.flagged",
    "t.dateToStart AS {0}".format(START_DATE),
    "t.inInbox AS {0}".format(IN_INBOX),
    "t.effectiveInInbox AS {0}".format(EFFECTIVE_IN_INBOX),
    "t.effectiveDateToStart AS {0}".format(EFFECTIVE_START_DATE),
    "t.childrenCountAvailable AS {0}".format(CHILD_COUNT),
    "t.blocked AS {0}".format(BLOCKED),
    "pi.status AS {0}".format(STATUS),
    "t.effectiveFlagged",
    "t.dateModified AS {0}".format(MODIFIED_DATE),
    "t.containingProjectInfo AS {0}".format(CONTAINING_PROJECT_INFO),
    "t.dateDue AS {0}".format(DUE_DATE)
    ]) + ", t.effectiveContainingProjectInfoRemaining AS {0}".format(PROJECT_IS_REMAINING)
TASK_FROM = ("((task tt left join projectinfo pi on tt.containingprojectinfo=pi.pk) t left join "
             "task p on t.task=p.persistentIdentifier) ")
TASK_WHERE = "(t.containingProjectInfo <> t.persistentIdentifier OR t.containingProjectInfo is NULL) "
TASK_NAME_WHERE = "t.dateCompleted IS NULL AND lower(t.name) LIKE lower('%{0}%') AND "
NOT_COMPLETED_CLAUSE = "t.dateCompleted IS NULL AND t.effectiveContainingProjectInfoRemaining = 1"
ACTIVE_CLAUSE = "t.blocked = 0 AND "
TAG_SELECT = ", ".join([
    "persistentIdentifier AS {0}".format(ID),
    "name AS {0}".format(NAME),
    "allowsNextAction AS {0}".format(ALLOWS_NEXT_ACTION)]) + ", availableTaskCount AS {0}".format(AVAILABLE_TASK_COUNT)
PROJECT_SELECT = ", ".join([
    "p.pk AS {0}".format(ID),
    "t.name AS {0}".format(NAME),
    "p.status AS {0}".format(STATUS),
    "p.numberOfAvailableTasks AS {0}".format(AVAILABLE_TASK_COUNT),
    "p.numberOfRemainingTasks AS {0}".format(REMAINING_TASK_COUNT),
    "p.containsSingletonActions AS {0}".format(SINGLETON),
    "f.name AS {0}".format(FOLDER_NAME),
    "t.dateToStart AS {0}".format(START_DATE)]) + ", t.effectiveDateToStart AS {0}".format(EFFECTIVE_START_DATE)

OF2_DUE_SOON_CONSTRAINT = " AND (t.isDueSoon or t.isOverdue)"
OF3_DUE_SOON_CONSTRAINT = " AND (t.dueSoon or t.overdue)"


def search_tasks(active_only, flagged, query, everything=None):
    where = (TASK_NAME_WHERE + TASK_WHERE).format(query)

    if active_only:
        where = "(t.blocked = 0 AND t.blockedByFutureStartDate = 0) AND " + where

    if flagged:
        where = "(t.flagged = 1 OR t.effectiveFlagged = 1) AND " + where

    if not everything:
        where = "(t.effectiveInInbox = 0 AND t.inInbox = 0) AND " + where

    return _generate_query(TASK_SELECT, TASK_FROM, where, "t." + NAME_SORT)


def search_inbox(query):
    where = "(t.effectiveInInbox = 1 OR t.inInbox = 1)"
    if query:
        where = (TASK_NAME_WHERE + where).format(query)
    return _generate_query(TASK_SELECT, TASK_FROM, where, "t." + NAME_SORT)


def search_projects(active_only, query):
    from_ = ("(ProjectInfo p LEFT JOIN Task t ON p.task=t.persistentIdentifier) "
             "LEFT JOIN Folder f ON p.folder=f.persistentIdentifier")
    where = "lower(t.name) LIKE lower('%{0}%')".format(query)
    order_by = "p.containsSingletonActions DESC, t.name ASC"

    if active_only:
        where = "p.status = 'active' AND " + where

    return _generate_query(PROJECT_SELECT, from_, where, order_by)


def search_tags(query):
    if not query:
        return "SELECT {0} FROM {1} ORDER BY {2}".format(TAG_SELECT, "Context", NAME_SORT)
    else:
        where = "lower(name) LIKE lower('%{0}%')".format(query)
        return _generate_query(TAG_SELECT, "Context", where, NAME_SORT)


def search_folders(query):
    select = "persistentIdentifier AS {0}, name as {1}".format(ID, NAME)
    where = "(dateHidden is null AND effectiveDateHidden is null)"
    if query:
        where = where + " AND lower(name) LIKE lower('%{0}%')".format(query)

    return _generate_query(select, "Folder", where, NAME_SORT)


def search_notes(active_only, flagged, query):
    select = TASK_SELECT + ", t.plainTextNote"
    where = "t.dateCompleted IS NULL AND lower(t.plainTextNote) LIKE lower('%{0}%')".format(query)

    if active_only:
        where = where + " AND (t.blocked = 0 AND t.blockedByFutureStartDate = 0)"

    if flagged:
        where = where + " AND (t.flagged = 1 OR t.effectiveFlagged = 1)"

    return _generate_query(select, TASK_FROM, where, "t." + NAME_SORT)


def show_recent_tasks(active_only):
    if active_only:
        return _generate_query(TASK_SELECT, TASK_FROM, NOT_COMPLETED_CLAUSE, "t.dateModified DESC") + " LIMIT 10"
    else:
        return "SELECT {0} FROM {1} ORDER BY {2} LIMIT {3}".format(TASK_SELECT, TASK_FROM, "t.dateModified DESC", 10)


def show_due_tasks():
    return _generate_query(TASK_SELECT, TASK_FROM, NOT_COMPLETED_CLAUSE + OF3_DUE_SOON_CONSTRAINT,
                           "t.dateDue ASC") + " LIMIT 10"


def _generate_query(select, from_, where, order_by):
    return "SELECT {0} FROM {1} WHERE {2} ORDER BY {3}".format(select, from_, where, order_by)
