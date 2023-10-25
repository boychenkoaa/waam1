# лес - фиктивное дерево
#
from collections import deque
from copy import copy, deepcopy

class Forest:
    def __init__(self, nodes):
        # для начала все - корни
        self._parents = dict()
        self._children = dict([(None, set())])
        self.nodes = set(nodes)
        for node in nodes:
            self.add(node, None)

    def __contains__(self, node):
        return item in self.nodes

    def add(self, node: int, parent:int):
        self.nodes.add(node)
        self._parents[node] = parent
        self._children[node] = set()
        self._children[parent].add(node)

    def rem(self, node):
        self.nodes.remove(node)
        # чистим детей
        self._children.pop(node)
        for key in self._children:
            if node in self._children[key]:
                self._children[key].remove(node)

        self._parents = {key: value for key, value in self._parents.items() if key != node}

        # чистим родителей

    def move(self, node, new_parent):
        self._children[self._parents[node]].remove(node)
        self._parents[node] = new_parent
        self._children[new_parent].add(node)

    def dfs(self, node=None):
        d = deque([node])
        ans = deque()
        while d:
            nd = d.pop()
            ans.append(nd)
            d.extend(self._children[nd])
        return list(ans)

    def raw(self):
        return {"parents": self._parents, "children": self._children}

    def str_subtree(self, node):
        def str_node(node1, level):
            if level == 0:
                return str(node1)+"\n"
            return (level - 1) * ".. " + str(node1) + "\n"

        d = deque([(node, 0)])
        ans = ""
        while d:
            nd, level = d.pop()
            ans += str_node(nd, level)
            d.extend([(child, level+1) for child in self._children[nd]])
        return ans

    def __str__(self):
        return self.str_subtree(None)

    def __repr__(self):
        return self.__str__()

    def children(self, node):
        return copy(self._children[node])

    def parent(self, node):
        return self._parents[node]

    def subtree(self, node):
        nodes = self.dfs(node)
        ans = Forest(nodes)
        [ans.move(node, self.parent(node)) for node in nodes]
        return ans

