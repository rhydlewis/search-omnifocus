__author__ = 'rlewis'


class Task(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __repr__(self):
        return "Task {0}, '{1}' (@{2}) in project '{3}' [{4}]".format(self.persistent_id, self.name, self.context,
                                                                      self.project, self.is_blocked)