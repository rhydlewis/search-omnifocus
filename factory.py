from __future__ import unicode_literals
import os
from datetime import datetime
from omnifocus import DEFAULT_PERSPECTIVES


class Item(object):
    def __init__(self, item_type, persistent_id, name, subtitle, icon):
        self.item_type = item_type
        self.name = name
        self.persistent_id = persistent_id
        self.subtitle = subtitle
        self.icon = icon

    def __repr__(self):
        return "{0}: {1}, ({2}), {3}, {4}".format(self.item_type, self.name, self.persistent_id,
                                                  self.subtitle, self.icon)


OF_ICON_ROOT = '/Applications/OmniFocus.app/Contents/Resources'
if not os.path.isdir(OF_ICON_ROOT):
    # see https://github.com/rhydlewis/search-omnifocus/issues/8
    OF_ICON_ROOT = '/Applications/OmniFocus.localized/OmniFocus.app/Contents/Resources'

ICON_DROPPED = os.path.join(OF_ICON_ROOT, 'dropped@2x.png')
ICON_FLAGGED = os.path.join(OF_ICON_ROOT, 'flagged@2x.png')
ICON_ON_HOLD = os.path.join(OF_ICON_ROOT, 'on-hold@2x.png')
ICON_ACTIVE = os.path.join(OF_ICON_ROOT, 'active-small@2x.png')
ICON_COMPLETED = os.path.join(OF_ICON_ROOT, 'completed@2x.png')
ICON_CONTEXT = os.path.join(OF_ICON_ROOT, 'quickopen-context@2x.png')
ICON_INBOX = os.path.join(OF_ICON_ROOT, 'tab-inbox-selected@2x.png')
ICON_PERSPECTIVE = os.path.join(OF_ICON_ROOT, 'Perspectives@2x.png')
ICON_DEFERRED = os.path.join('.', 'deferred.png')
ICON_FOLDER = os.path.join(OF_ICON_ROOT, 'quickopen-folder@2x.png')

ICON_PERSPECTIVE_INBOX = os.path.join(OF_ICON_ROOT, 'tab-inbox-selected@2x.png')
ICON_PERSPECTIVE_PROJECTS = os.path.join(OF_ICON_ROOT, 'tab-projects-selected@2x.png')
ICON_PERSPECTIVE_CONTEXTS = os.path.join(OF_ICON_ROOT, 'tab-contexts-selected@2x.png')
ICON_PERSPECTIVE_FORECAST = os.path.join(OF_ICON_ROOT, 'tab-forecast-selected@2x.png')
ICON_PERSPECTIVE_FLAGGED = os.path.join(OF_ICON_ROOT, 'tab-flagged-selected@2x.png')
ICON_PERSPECTIVE_REVIEW = os.path.join(OF_ICON_ROOT, 'tab-review-selected@2x.png')

DEFAULT_PERSPECTIVE_ICONS = [ICON_PERSPECTIVE_INBOX, ICON_PERSPECTIVE_PROJECTS,
                             ICON_PERSPECTIVE_CONTEXTS, ICON_PERSPECTIVE_FORECAST,
                             ICON_PERSPECTIVE_FLAGGED, ICON_PERSPECTIVE_REVIEW]

ICON_LOOKUP = dict(zip(DEFAULT_PERSPECTIVES, DEFAULT_PERSPECTIVE_ICONS))

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

    return Item(item_type='Project', persistent_id=pid, name=name, icon=icon, subtitle=folder)


def create_task(raw_data):
    pid = raw_data[0]
    # completed = raw_data[2] == 1
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

    return Item(item_type='Task', persistent_id=pid, name=name, icon=icon, subtitle=project)


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

    return Item(item_type='Context', persistent_id=pid, name=name, icon=icon, subtitle=subtitle)


def create_perspective(name):
    icon = ICON_PERSPECTIVE
    perspective_type = 'Custom'
    if name in DEFAULT_PERSPECTIVES:
        icon = ICON_LOOKUP[name]
        perspective_type = 'Default'

    return Item(item_type='Perspective', persistent_id='', name=name, icon=icon,
                subtitle="Omnifocus {0} Perspective".format(perspective_type))


def create_folder(raw_data):
    pid = raw_data[0]
    name = raw_data[1]

    return Item(item_type='Folder', persistent_id=pid, name=name, icon=ICON_FOLDER, subtitle='')


def deferred_date(datetostart, effectivedatetostart):
    if effectivedatetostart == 0:
        return datetostart


def is_deferred(datetostart):
    deferred = False
    if datetostart is not None:
        dts = datetime.fromtimestamp(datetostart + 978307200)
        if dts > datetime.now():
            deferred = True

    return deferred

