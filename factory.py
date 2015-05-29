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
ICON_DEFERRED = os.path.join('.', 'deferred.png')

PROJECT_ICONS = {'active': ICON_ACTIVE, 'done': ICON_COMPLETED, 'dropped': ICON_DROPPED, 'inactive': ICON_ON_HOLD}


def create_project(raw_data):
    pid = raw_data[0]
    name = raw_data[1]
    status = raw_data[2]
    folder = raw_data[6]
    datetostart = raw_data[7]
    icon = PROJECT_ICONS[status]

    if status == 'active' and is_deferred(datetostart):
        icon = ICON_DEFERRED

    return Project(persistent_id=pid, name=name, status=status, icon=icon, subtitle=folder)


def create_task(raw_data):
    pid = raw_data[0]
    completed = raw_data[2] == 1
    blocked = raw_data[3] == 1
    name = raw_data[1]
    project = raw_data[5]
    inbox = (raw_data[8] == 1 or raw_data[9] == 1)
    datetostart = raw_data[7]

    icon = ICON_ACTIVE

    if blocked:
        icon = ICON_ON_HOLD
    if is_deferred(datetostart):
        icon = ICON_DEFERRED
    if inbox:
        icon = ICON_INBOX

    return Task(persistent_id=pid, name=name, is_complete=completed, is_blocked=blocked,
                context=raw_data[4], subtitle=project, in_inbox=inbox, icon=icon, datetostart=datetostart)


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


class Task(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __repr__(self):
        return "Task {0}, '{1}' (@{2}) in project '{3}' [{4}]".format(self.persistent_id, self.name, self.context,
                                                                      self.subtitle, self.is_blocked)