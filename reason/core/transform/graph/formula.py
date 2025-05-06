import networkx as nx

from hashlib import sha256

from reason.core.fof_types import Const, Function, LogicConnective, LogicQuantifier, Predicate, Variable
from reason.tools.graph import IsomorphismLab
from reason.core.fof import *
from reason.parser.tree import *


class FormulaToGraphLab:
    def __init__(self, formula, skolem_prefix="s"):
        self.skolem_prefix = skolem_prefix
        self.graph = nx.DiGraph()
        self.translate = {}
        self.translate_inv = {}
        self.node_color_map = {}
        self.edge_color_map = {}

        self._transform(formula)
        self.signature = self._signature()
        self.sha256 = sha256(repr(self.signature).encode("utf-8")).hexdigest()

    def update_edge_arg_idx(self, n, m, i):
        if self.graph.has_edge(n, m):
            arg_idx = list(self.edge_color_map[n, m])
            arg_idx.append(i + 1)
            arg_idx.sort()
            self.edge_color_map[n, m] = tuple(arg_idx)
        else:
            self.graph.add_edge(n, m)
            self.edge_color_map[n, m] = (i + 1,)

    def add_node(self, n, color=None):
        self.graph.add_node(n)
        if color is not None:
            self.node_color_map[n] = color

    def add_edge(self, n, m, color=None):
        self.graph.add_edge(n, m)
        if color is not None:
            self.edge_color_map[n, m] = color

    def get_form_id(self, form):
        if form in self.translate:
            return self.translate[form]
        else:
            res = len(self.translate) + 1
            self.translate[form] = res
            self.translate_inv[res] = form
            return res

    def _signature(self):
        iso_lab = IsomorphismLab(
            graph=self.graph, nodes_color_map=self.node_color_map, edges_color_map=self.edge_color_map
        )
        res = iso_lab.signature()
        return res

    def _transform(self, value):
        if value in self.translate:
            return self.translate[value]

        match value:
            case Variable():
                node = self.get_form_id(value)
                self.add_node(node, color="Variable")
                return node

            case Const(name=name):
                node = self.get_form_id(value)
                self.add_node(node, color=f"Const:{name}")
                return node

            case Function(name=name, args=args):
                node = self.get_form_id(value)
                self.add_node(node, color=f"Function:{name}")

                for i, n in enumerate(map(self._transform, args)):
                    self.update_edge_arg_idx(n, node, i)

                return node

            case Predicate(name=name, args=args) if name == EQ:
                node = self.get_form_id(value)
                self.add_node(node, color=f"Predicate:{name}")

                for i, n in enumerate(map(self._transform, args)):
                    self.graph.add_edge(n, node)

                return node

            case Predicate(name=name, args=args):
                node = self.get_form_id(value)
                self.add_node(node, color=f"Predicate:{name}")

                for i, n in enumerate(map(self._transform, args)):
                    self.update_edge_arg_idx(n, node, i)

                return node

            case LogicConnective(name=op, args=[a, b]) if op in {AND, OR, IFF}:
                node = self.get_form_id(value)
                self.add_node(node, color=op)

                self.add_edge(self._transform(a), node)
                self.add_edge(self._transform(b), node)

                return node

            case LogicConnective(name=op, args=args):
                node = self.get_form_id(value)
                self.add_node(node, color=op)

                for i, n in enumerate(map(self._transform, args)):
                    self.update_edge_arg_idx(n, node, i)

                return node

            case LogicQuantifier(name=op, args=[var, arg]):
                node = self.get_form_id(value)
                arg_node = self._transform(arg)
                var_node = self._transform(var)
                if self.node_color_map[arg_node] == op:
                    self.add_edge(var_node, arg_node)
                    return arg_node
                else:
                    self.add_node(node, color=op)
                    self.add_edge(var_node, node)
                    self.add_edge(arg_node, node)

                    return node
                
    def get_graph_repr(self):
        graph = nx.DiGraph()
        for n in self.graph.nodes:
            graph.add_node(n, name=str(self.node_color_map[n]))

        for n, m in self.graph.edges:
            if (n, m) in self.edge_color_map:
                graph.add_edge(n, m, name=str(self.edge_color_map[n, m]))
            else:
                graph.add_edge(n, m)

        return graph 

