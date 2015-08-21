from __future__ import unicode_literals
import os
from datetime import datetime

OF_ICON_ROOT = '/Applications/OmniFocus.app/Contents/Resources'

ICON_DROPPED = os.path.join(OF_ICON_ROOT, 'dropped@2x.png')
ICON_FLAGGED = os.path.join(OF_ICON_ROOT, 'flagged@2x.png')
ICON_ON_HOLD = os.path.join(OF_ICON_ROOT, 'on-hold@2x.png')
ICON_ACTIVE = os.path.join(OF_ICON_ROOT, 'active-small@2x.png')
ICON_COMPLETED = os.path.join(OF_ICON_ROOT, 'completed@2x.png')
ICON_CONTEXT = os.path.join(OF_ICON_ROOT, 'quickopen-context@2x.png')
ICON_INBOX = os.path.join(OF_ICON_ROOT, 'tab-inbox-selected@2x.png')
ICON_PERSPECTIVE = os.path.join(OF_ICON_ROOT, 'Perspectives@2x.png')
ICON_DEFERRED = os.path.join('.', 'deferred.png')

ACTIVE = 'active'
DONE = 'done'
DROPPED = 'dropped'
INACTIVE = 'inactive'

PROJECT_ICONS = {ACTIVE: ICON_ACTIVE, DONE: ICON_COMPLETED, DROPPED: ICON_DROPPED,
                 INACTIVE: ICON_ON_HOLD}
CONTEXT_ICONS = {1: ICON_ACTIVE, 0: ICON_ON_HOLD}


def create_project(raw_data):
    pid = raw_data[0]
    name = raw_data[1]
    status = raw_data[2]
    folder = raw_data[6]
    datetostart = deferred_date(raw_data[7], raw_data[8])

    icon = PROJECT_ICONS[status]

    if status == 'active' and is_deferred(datetostart):
        icon = ICON_DEFERRED

    return Project(persistent_id=pid, name=name, status=status, icon=icon, subtitle=folder)


def create_task(raw_data):
    pid = raw_data[0]
    completed = raw_data[2] == 1
    blocked_by_future_date = raw_data[3] == 1
    name = raw_data[1]
    project = raw_data[5]
    inbox = (raw_data[8] == 1 or raw_data[9] == 1)
    datetostart = deferred_date(raw_data[7], raw_data[10])

    blocked = raw_data[11] == 1
    children = raw_data[12]
    parent_status = raw_data[13]

    icon = ICON_ACTIVE

    if blocked_by_future_date or (blocked and not children) or parent_status != ACTIVE:
        icon = ICON_ON_HOLD
    if is_deferred(datetostart):
        icon = ICON_DEFERRED
    if inbox:
        icon = ICON_INBOX

    return Task(persistent_id=pid, name=name, is_complete=completed, is_blocked=blocked,
                context=raw_data[4], subtitle=project, in_inbox=inbox, icon=icon,
                datetostart=datetostart)


def create_context(raw_data):
    pid = raw_data[0]
    name = raw_data[1]
    allows_next_action = raw_data[2]
    available_tasks = raw_data[4]
    if available_tasks == 1:
        subtitle = "1 task available"
    else:
        subtitle = "{0} tasks available".format(available_tasks)

    icon = CONTEXT_ICONS[allows_next_action]

    return Context(persistent_id=pid, name=name, status=allows_next_action, icon=icon,
                   subtitle=subtitle)


def create_perspective(name):
    return Perspective(name=name, icon=ICON_PERSPECTIVE, subtitle="Omnifocus Perspective")


def deferred_date(datetostart, effectivedatetostart):
    d = effectivedatetostart
    if d == 0:
        d = datetostart
    return d


def is_deferred(datetostart):
    deferred = False
    if datetostart is not None:
        dts = datetime.fromtimestamp(datetostart + 978307200)
        if dts > datetime.now():
            deferred = True

    return deferred


class Project(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __repr__(self):
        return "Project {0}, '{1}' [{2}]".format(self.persistent_id, self.name, self.status)


class Context(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __repr__(self):
        return "Context {0}, '{1}' [{2}]".format(self.persistent_id, self.name, self.status)


class Task(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __repr__(self):
        return "Task {0}, '{1}' (@{2}) in project '{3}' [{4}]".\
            format(self.persistent_id, self.name, self.context, self.subtitle, self.is_blocked)

class Perspective(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __repr__(self):
        return "Perspective {0}".format(self.name)
