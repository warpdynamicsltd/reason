import networkx as nx

from reason.core.fof import *


class FormulaToGraphLab:
    def __init__(self, formula, skolem_prefix="s"):
        self.skolem_prefix = skolem_prefix
        self.graph = nx.Graph()
        self.translate = {}
        self.translate_inv = {}

        self._transform(formula)

    def get_form_id(self, form):
        if form in self.translate:
            return self.translate[form]
        else:
            res = len(self.translate) + 1
            self.translate[form] = res
            self.translate_inv[res] = form
            return res

    def _transform(self, formula):
        match formula:
            case Variable():
                self.graph.add_node(formula, type="Variable")
                return formula
            case Const():
                self.graph.add_node(formula, type="Const")
                return formula

            case Function(name=name, args=args) if name[: len(self.skolem_prefix)] == self.skolem_prefix:
                node = self.get_form_id(formula)
                self.graph.add_node(node, type="Function")
                for n in map(self._transform, args):
                    self.graph.add_edge(node, n)

                return node

            case Function(name=name, args=args) if name[: len(self.skolem_prefix)] != self.skolem_prefix:
                node = self.get_form_id(formula)
                self.graph.add_node(node, type="Function")
                for i, n in enumerate(map(self._transform, args)):
                    self.graph.add_edge(node, n, arg_idx=i + 1)

                return node

            case Predicate(args=args):
                node = self.get_form_id(formula)
                self.graph.add_node(node, type="Predicate")
                for i, n in enumerate(map(self._transform, args)):
                    self.graph.add_edge(node, n, arg_idx=i + 1)

                return node
