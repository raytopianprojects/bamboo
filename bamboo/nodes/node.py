nodes = {}
from panda3d.core import NodePath
from bamboo.showbase.show_base_global import render2d, aspect2d, globalClock, cvMgr, hidden, builtins


class Node(NodePath):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        nodes[self.node()] = self

        if "parent" in kwargs:
            if kwargs["parent"]:
                self.reparent_to(kwargs["parent"])
        else:
            self.reparent_to(builtins.render)

    @property
    def x(self):
        return self.get_x()

    @x.setter
    def x(self, value):
        self.set_x(value)

    @property
    def y(self):
        return self.get_y()

    @y.setter
    def y(self, value):
        self.set_y(value)

    @property
    def z(self):
        return self.get_z()

    @z.setter
    def z(self, value):
        self.set_z(value)

    @property
    def h(self):
        return self.get_h()

    @h.setter
    def h(self, value):
        self.set_h(value)

    @property
    def p(self):
        return self.p()

    @p.setter
    def p(self, value):
        self.set_p(value)

    @property
    def r(self):
        return self.get_r()

    @r.setter
    def r(self, value):
        self.set_r(value)

    @property
    def sx(self):
        return self.get_sx()

    @sx.setter
    def sx(self, value):
        self.set_sx(value)

    @property
    def sy(self):
        return self.sy()

    @sy.setter
    def sy(self, value):
        self.set_sy(value)

    @property
    def sz(self):
        return self.get_sz()

    @sz.setter
    def sz(self, value):
        self.set_sz(value)

    def clean_up(self):
        del nodes[self.node()]
        self.remove_node()

    def find(self, path: str):
        node = NodePath.find(self, path)

        if node in nodes:
            return nodes[node]
        else:
            return node

    def find_nodepath(self, path: str):
        return NodePath.find(self, path)

    def find_all_matches(self, path: str):
        nodepaths = NodePath.find_all_matches(self, path)

        found_nodes = []
        for node in nodepaths:
            if node.node() in nodes:
                found_nodes.append(nodes[node.node()])
            print(node, node in nodes)

        return found_nodes, nodepaths

    def find_all_nodepath_matches(self, path: str):
        return NodePath.find_all_matches(self, path)

    @property
    def children(self):
        return [nodes[child.node()] for child in NodePath.getChildren(self) if child.node() in nodes]

    @property
    def children_nodepaths(self):
        return self.get_children()

    def parent(self):
        parent_node = NodePath.get_parent(self).node()
        return nodes[NodePath.get_parent(self).node()] if parent_node in nodes else NodePath.get_parent(self)


from panda3d.core import LODNode, FadeLODNode


class Lod(Node):
    def __init__(self, name: str, fades=False, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

        if not fades:
            self._lod_node = LODNode()
        else:
            self._lod_node = FadeLODNode()
        self._lod_node_path = NodePath(self._lod_node)
        self._lod_node_path.reparent_to(self)

    def add_level(self, closest: float, furthest: float):
        self._lod_node.add_switch(furthest, closest)

    @property
    def center(self):
        return self._lod_node.get_center()

    @center.setter
    def center(self, value):
        self._lod_node.set_center(value)
