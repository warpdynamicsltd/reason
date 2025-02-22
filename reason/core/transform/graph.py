import networkx as nx

from reason.core.fof import *

class FormulaToGraphLab:
    def __init__(self, formula, skolem_prefix="s"):
        self.skolem_prefix = skolem_prefix
        self.graph = nx.Graph()
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
            case Variable(name=name):
                self.graph.add_node(formula, color='Variable')
                return formula
            case Const(name=name):
                self.graph.add_node(formula, color='Const')
                return formula

            case Function(name=name, args=args):
                node = self.get_form_id(form)
                self.graph.add_node(node, color='Function')
                for n in map(self._transform, args):
                    self.graph.add_edge(node, n)

                return node




