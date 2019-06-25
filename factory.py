from __future__ import unicode_literals
import os
from datetime import datetime
from omnifocus import DEFAULT_OF2_PERSPECTIVES, DEFAULT_OF3_PERSPECTIVES, DEFAULT_OF_VERSION
from workflow import ICON_WARNING
from queries import ALLOWS_NEXT_ACTION, AVAILABLE_TASK_COUNT, BLOCKED, BLOCKED_BY_START_DATE, CHILD_COUNT, \
    DUE_DATE, EFFECTIVE_IN_INBOX, EFFECTIVE_START_DATE, FOLDER_NAME, ID, IN_INBOX, NAME, PROJECT_NAME, START_DATE, \
    STATUS, CONTAINING_PROJECT_INFO, MODIFIED_DATE

STATUS_ACTIVE = 'active'
STATUS_DONE = 'done'
STATUS_DROPPED = 'dropped'
STATUS_INACTIVE = 'inactive'
DATETIME_OFFSET = 978307200

FOLDER_PREFIX = 'en.lproj/OmniFocus Help/art/'


class Item(object):
    def __init__(self, item_type, persistent_id, name, subtitle, icon):
        self.item_type = item_type
        self.name = name
        self.persistent_id = persistent_id
        self.subtitle = subtitle
        self.icon = icon

    def __repr__(self):
        return "{0}: {1}, ({2}), {3}, {4}".format(self.item_type, self.name, self.persistent_id, self.subtitle,
                                                  self.icon)


class Factory:
    def __init__(self, icon_root, version):
        use_of_2 = version != DEFAULT_OF_VERSION

        self.dropped_icon = os.path.join(icon_root, 'dropped@2x.png')
        self.flagged_icon = os.path.join(icon_root, 'flagged@2x.png')
        self.on_hold_icon = os.path.join(icon_root, 'on-hold@2x.png')
        self.active_icon = os.path.join(icon_root, 'active-small@2x.png')
        self.completed_icon = os.path.join(icon_root, 'completed@2x.png')
        self.inbox_icon = os.path.join(icon_root, 'inbox-sidebar@2x.png')
        self.perspective_icon = os.path.join(icon_root, 'Perspectives@2x.png')
        self.deferred_icon = os.path.join('.', 'deferred.png')
        self.folder_icon = os.path.join(icon_root, 'quickopen-folder@2x.png')

        self.setup_perspective_icons(icon_root, use_of_2)

        if use_of_2:
            self.icon_lookup = dict(zip(DEFAULT_OF2_PERSPECTIVES, self.default_perspective_icons))
        else:
            self.icon_lookup = dict(zip(DEFAULT_OF3_PERSPECTIVES, self.default_perspective_icons))

        self.project_icons = {STATUS_ACTIVE: self.active_icon, STATUS_DONE: self.completed_icon,
                              STATUS_DROPPED: self.dropped_icon, STATUS_INACTIVE: self.on_hold_icon}
        self.context_icons = {1: self.active_icon, 0: self.on_hold_icon}

    def setup_perspective_icons(self, icon_root, use_of_2):
        if use_of_2:
            self.context_icon = os.path.join(icon_root, 'quickopen-context@2x.png')
            self.inbox_perspective_icon = os.path.join(icon_root, 'tab-inbox-selected@2x.png')
            self.projects_perspective_icon = os.path.join(icon_root, 'tab-projects-selected@2x.png')
            self.contexts_perspective_icon = os.path.join(icon_root, 'tab-contexts-selected@2x.png')
            self.forecast_perspective_icon = os.path.join(icon_root, 'tab-forecast-selected@2x.png')
            self.flagged_perspective_icon = os.path.join(icon_root, 'tab-flagged-selected@2x.png')
            self.review_perspective_icon = os.path.join(icon_root, 'tab-review-selected@2x.png')
        else:
            self.context_icon = os.path.join(icon_root, 'quickopen-tag@2x.png')
            self.inbox_perspective_icon = os.path.join(icon_root, 'AppIcon-Credits.png')
            self.projects_perspective_icon = os.path.join(icon_root, 'AppIcon-Credits.png')
            self.contexts_perspective_icon = os.path.join(icon_root, 'AppIcon-Credits.png')
            self.forecast_perspective_icon = os.path.join(icon_root, 'AppIcon-Credits.png')
            self.flagged_perspective_icon = os.path.join(icon_root, 'AppIcon-Credits.png')
            self.review_perspective_icon = os.path.join(icon_root, 'AppIcon-Credits.png')

        self.default_perspective_icons = [self.inbox_perspective_icon, self.projects_perspective_icon,
                                          self.contexts_perspective_icon, self.forecast_perspective_icon,
                                          self.flagged_perspective_icon, self.review_perspective_icon]

    def create_project(self, row):
        pid = row[ID]
        name = row[NAME]
        status = row[STATUS]
        folder = row[FOLDER_NAME]
        datetostart = deferred_date(row[START_DATE], row[EFFECTIVE_START_DATE])
    
        icon = self.project_icons[status]
    
        if status == 'active' and is_deferred(datetostart):
            icon = self.deferred_icon
    
        return Item(item_type='Project', persistent_id=pid, name=name, icon=icon, subtitle=folder)
    
    def create_task(self, row):
        pid = row[ID]
        blocked_by_future_date = row[BLOCKED_BY_START_DATE] == 1
        name = row[NAME]
        project = row[PROJECT_NAME]
        inbox = (row[IN_INBOX] == 1 or row[EFFECTIVE_IN_INBOX] == 1)
        datetostart = deferred_date(row[START_DATE], row[EFFECTIVE_START_DATE])
    
        blocked = row[BLOCKED] == 1
        children = row[CHILD_COUNT]
        parent_status = row[STATUS]
        due_date = None

        icon = self.active_icon
    
        if blocked_by_future_date or (blocked and not children) or parent_status != STATUS_ACTIVE:
            icon = self.on_hold_icon
        if is_deferred(datetostart):
            icon = self.deferred_icon
        if inbox:
            icon = self.inbox_icon
    
        if row[DUE_DATE]:
            due_date = offset_date(row[DUE_DATE])
            now = datetime.now()
            due_date_label = due_date.strftime("%c")

            if now > due_date:
                name = name + " (overdue: {0})".format(due_date_label)
                icon = ICON_WARNING
            else:
                name = name + " (due: {0})".format(due_date_label)

        return Item(item_type='Task', persistent_id=pid, name=name, icon=icon, subtitle=project)
    
    def create_context(self, raw_data):
        pid = raw_data[ID]
        name = raw_data[NAME]
        allows_next_action = raw_data[ALLOWS_NEXT_ACTION]
        available_tasks = raw_data[AVAILABLE_TASK_COUNT]
        if available_tasks == 1:
            subtitle = "1 task available"
        else:
            subtitle = "{0} tasks available".format(available_tasks)
    
        icon = self.context_icons[allows_next_action]
    
        return Item(item_type='Context', persistent_id=pid, name=name, icon=icon, subtitle=subtitle)
    
    def create_perspective(self, name):
        icon = self.perspective_icon
        perspective_type = 'Custom'
        if name in DEFAULT_OF2_PERSPECTIVES or name in DEFAULT_OF3_PERSPECTIVES:
            icon = self.icon_lookup[name]
            perspective_type = 'Default'
    
        return Item(item_type='Perspective', persistent_id='', name=name, icon=icon,
                    subtitle="Omnifocus {0} Perspective".format(perspective_type))
    
    def create_folder(self, row):
        pid = row[ID]
        name = row[NAME]

        return Item(item_type='Folder', persistent_id=pid, name=name, icon=self.folder_icon,
                    subtitle='')

    def create_recent_item(self, raw_data):
        task = self.create_task(raw_data)

        if raw_data[ID] == raw_data[CONTAINING_PROJECT_INFO]:
            task.name = task.name + " (Project)"
        else:
            task.name = task.name + " (Task)"

        modified_date = offset_date(raw_data[MODIFIED_DATE]).strftime("%c")
        task.subtitle = modified_date
        return task


def deferred_date(datetostart, effectivedatetostart):
    if effectivedatetostart == 0:
        return datetostart


def is_deferred(datetostart):
    deferred = False
    if datetostart is not None:
        dts = offset_date(datetostart)
        if dts > datetime.now():
            deferred = True

    return deferred

def offset_date(value):
    return datetime.fromtimestamp(value + DATETIME_OFFSET)
