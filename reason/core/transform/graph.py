import networkx as nx

from hashlib import sha256

from reason.tools.graph import IsomorphismLab
from reason.core.fof import *
from reason.parser.tree import *


class FormulaToGraphLab:
    def __init__(self, formula, skolem_prefix="s"):
        self.skolem_prefix = skolem_prefix
        self.graph = nx.Graph()
        self.translate = {}
        self.translate_inv = {}

        self._transform(formula)
        self.sha256 = sha256(repr(self._signature()).encode("utf-8")).hexdigest()

    def get_form_id(self, form):
        if form in self.translate:
            return self.translate[form]
        else:
            res = len(self.translate) + 1
            self.translate[form] = res
            self.translate_inv[res] = form
            return res

    def update_edge(self, node, n, i):
        if self.graph.has_edge(node, n):
            arg_idx = list(self.graph[node][n]["arg_idx"])
            arg_idx.append(i + 1)
            arg_idx.sort()
            self.graph[node][n]["arg_idx"] = tuple(arg_idx)
        else:
            self.graph.add_edge(node, n, arg_idx=(i + 1,))

    def _signature(self):
        nodes_color_map = nx.get_node_attributes(self.graph, "type")
        edges_color_map = nx.get_edge_attributes(self.graph, "arg_idx")
        edges_color_map.update(nx.get_edge_attributes(self.graph, "type"))
        edges_color_map = {k: repr(edges_color_map[k]) for k in edges_color_map.keys()}
        # print(nodes_color_map)
        # print(edges_color_map)
        iso_lab = IsomorphismLab(graph=self.graph, nodes_color_map=nodes_color_map,edges_color_map=edges_color_map)
        res = iso_lab.signature()
        return res


    def _transform(self, value):
        if value in self.translate:
            return self.translate[value]

        match value:
            case Variable():
                node = self.get_form_id(value)
                self.graph.add_node(node, type="Variable")
                return node

            case Const(name=name):
                name_node = self.get_form_id(name)
                self.graph.add_node(name_node, type=f"{name}")

                node = self.get_form_id(value)
                self.graph.add_edge(name_node, node, type="Name")
                self.graph.add_node(node, type="Const")
                return node

            case Function(name=name, args=args) if name[: len(self.skolem_prefix)] == self.skolem_prefix:
                node = self.get_form_id(value)
                self.graph.add_node(node, type="SFunction")
                for n in map(self._transform, args):
                    self.graph.add_edge(node, n)

                return node

            case Function(name=name, args=args) if name[: len(self.skolem_prefix)] != self.skolem_prefix:
                name_node = self.get_form_id(name)
                self.graph.add_node(name_node, type=f"{name}")

                node = self.get_form_id(value)
                self.graph.add_edge(name_node, node, type="Name")

                self.graph.add_node(node, type="Function")
                for i, n in enumerate(map(self._transform, args)):
                    self.update_edge(node, n, i)

                return node

            case Predicate(name=name, args=args) if name == EQ:
                name_node = self.get_form_id(name)
                self.graph.add_node(name_node, type=f"{name}")

                node = self.get_form_id(value)
                self.graph.add_edge(name_node, node, type="Name")

                self.graph.add_node(node, type="Predicate")
                for i, n in enumerate(map(self._transform, args)):
                    self.graph.add_edge(node, n, type="EQ-arg")

                return node

            case Predicate(name=name, args=args):
                name_node = self.get_form_id(name)
                self.graph.add_node(name_node, type=f"{name}")

                node = self.get_form_id(value)
                self.graph.add_edge(name_node, node, type="Name")

                self.graph.add_node(node, type="Predicate")
                for i, n in enumerate(map(self._transform, args)):
                    self.update_edge(node, n, i)

                return node

            case (*args,) if all(isinstance(arg, AbstractTerm) for arg in args):
                node = self.get_form_id(value)
                self.graph.add_node(node, type="Addend")
                for i, n in enumerate(map(self._transform, args)):
                    self.graph.add_edge(node, n)

                return node

            case (*args,) if all(type(arg) is tuple for arg in args):
                node = self.get_form_id(value)
                self.graph.add_node(node, type="Root")
                for i, n in enumerate(map(self._transform, args)):
                    self.graph.add_edge(node, n)

                return node

            case (1,):
                node = self.get_form_id(value)
                self.graph.add_node(node, type="Truth")

                return node

        raise Exception(f"unexpected value {value}")
