from __future__ import unicode_literals
import os
from datetime import datetime
from omnifocus import DEFAULT_PERSPECTIVES

ACTIVE = 'active'
DONE = 'done'
DROPPED = 'dropped'
INACTIVE = 'inactive'


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


class Factory:
    def __init__(self, icon_root):
        self.dropped_icon = os.path.join(icon_root, 'dropped@2x.png')
        self.flagged_icon = os.path.join(icon_root, 'flagged@2x.png')
        self.on_hold_icon = os.path.join(icon_root, 'on-hold@2x.png')
        self.active_icon = os.path.join(icon_root, 'active-small@2x.png')
        self.completed_icon = os.path.join(icon_root, 'completed@2x.png')
        self.context_icon = os.path.join(icon_root, 'quickopen-context@2x.png')
        self.inbox_icon = os.path.join(icon_root, 'tab-inbox-selected@2x.png')
        self.perspective_icon = os.path.join(icon_root, 'Perspectives@2x.png')
        self.deferred_icon = os.path.join('.', 'deferred.png')
        self.folder_icon = os.path.join(icon_root, 'quickopen-folder@2x.png')
        
        self.inbox_perspective_icon = os.path.join(icon_root, 'tab-inbox-selected@2x.png')
        self.projects_perspective_icon = os.path.join(icon_root, 'tab-projects-selected@2x.png')
        self.contexts_perspective_icon = os.path.join(icon_root, 'tab-contexts-selected@2x.png')
        self.forecast_perspective_icon = os.path.join(icon_root, 'tab-forecast-selected@2x.png')
        self.flagged_perspective_icon = os.path.join(icon_root, 'tab-flagged-selected@2x.png')
        self.review_perspective_icon = os.path.join(icon_root, 'tab-review-selected@2x.png')
        
        self.default_perspective_icons = [self.inbox_perspective_icon,
                                          self.projects_perspective_icon,
                                          self.contexts_perspective_icon,
                                          self.forecast_perspective_icon,
                                          self.flagged_perspective_icon,
                                          self.review_perspective_icon]
        
        self.icon_lookup = dict(zip(DEFAULT_PERSPECTIVES, self.default_perspective_icons))

        self.project_icons = {ACTIVE: self.active_icon, DONE: self.completed_icon,
                              DROPPED: self.dropped_icon, INACTIVE: self.on_hold_icon}
        self.context_icons = {1: self.active_icon, 0: self.on_hold_icon}
    
    def create_project(self, raw_data):
        pid = raw_data[0]
        name = raw_data[1]
        status = raw_data[2]
        folder = raw_data[6]
        datetostart = deferred_date(raw_data[7], raw_data[8])
    
        icon = self.project_icons[status]
    
        if status == 'active' and is_deferred(datetostart):
            icon = self.deferred_icon
    
        return Item(item_type='Project', persistent_id=pid, name=name, icon=icon, subtitle=folder)
    
    def create_task(self, raw_data):
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
    
        icon = self.active_icon
    
        if blocked_by_future_date or (blocked and not children) or parent_status != ACTIVE:
            icon = self.on_hold_icon
        if is_deferred(datetostart):
            icon = self.deferred_icon
        if inbox:
            icon = self.inbox_icon
    
        return Item(item_type='Task', persistent_id=pid, name=name, icon=icon, subtitle=project)
    
    def create_context(self, raw_data):
        pid = raw_data[0]
        name = raw_data[1]
        allows_next_action = raw_data[2]
        available_tasks = raw_data[4]
        if available_tasks == 1:
            subtitle = "1 task available"
        else:
            subtitle = "{0} tasks available".format(available_tasks)
    
        icon = self.context_icons[allows_next_action]
    
        return Item(item_type='Context', persistent_id=pid, name=name, icon=icon, subtitle=subtitle)
    
    def create_perspective(self, name):
        icon = self.perspective_icon
        perspective_type = 'Custom'
        if name in DEFAULT_PERSPECTIVES:
            icon = self.icon_lookup[name]
            perspective_type = 'Default'
    
        return Item(item_type='Perspective', persistent_id='', name=name, icon=icon,
                    subtitle="Omnifocus {0} Perspective".format(perspective_type))
    
    def create_folder(self, raw_data):
        pid = raw_data[0]
        name = raw_data[1]

        return Item(item_type='Folder', persistent_id=pid, name=name, icon=self.folder_icon, subtitle='')


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

