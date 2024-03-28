from bamboo.nodes.node import Node
from bamboo.showbase.direct_object import DirectObject


class Mob(Node, DirectObject):
    def __init__(self, name: str, update=NotImplemented, active=True, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self._listening = {}
        self._tasks = {}

        self.update = update

        if self.update != NotImplemented:
            self.add_task(self.update)

        self.active = active

        if not self.active:
            self.disable()

    def add_task(self, funcOrTask, name=None, sort=None, extraArgs=None, priority=None, appendTask=False,
                 uponDeath=None, taskChain=None, delay=None):
        DirectObject.add_task(self, funcOrTask,
                              name=None,
                              sort=None,
                              extraArgs=None,
                              priority=None,
                              appendTask=False,
                              uponDeath=None,
                              taskChain=None,
                              delay=None)
        self._tasks[funcOrTask] = ([name, sort, extraArgs, priority, appendTask, uponDeath, taskChain,
                                    delay])

    def accept(self, event, method, extraArgs=None):
        DirectObject.accept(self, event, method, extraArgs=extraArgs)

        self._listening["event"] = [method, extraArgs]

    def disable(self):
        self.active = False
        self.ignore_all()
        self.remove_all_tasks()

    def enable(self):
        self.active = True
        for event, values in self._listening.items():
            self.accept(event, values[0], values[1])

        for funcOrTask, values in self._tasks.items():
            self.add_task(funcOrTask, *values)

    def toggle(self):
        if self.active:
            self.disable()
        else:
            self.enable()

    def clean_up(self):
        Node.clean_up(self)

        del self._listening
        del self._tasks

        self.ignore_all()
        self.remove_all_tasks()
