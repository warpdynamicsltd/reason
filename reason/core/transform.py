from copy import deepcopy
from reason.core import immutable_copy, n_nodes, AbstractTerm, AbstractTermMutable

def explode_over_conjunctions(formula):
  stack = []

  node = formula
  stack.append((None, None, None, node))
  root = None
  results_set = set()

  while stack:
    cparent, parent, index, node = stack.pop(-1)
    cnode = AbstractTermMutable(node.name)
    stack += [(cnode, node, i, arg) for i, arg in reversed(list(enumerate(node.args)))]

    if parent is None:
      root = cnode
    else:
      cparent.args.append(cnode)

    match node:
      case AbstractTerm(name="CONJUNCTION"):
        for k in range(len(node.args)):
          cnode.args = node.args[:k + 1]
          obj = deepcopy(root)
          formula = immutable_copy(obj)
          if formula not in results_set:
            results_set.add(formula)
        cnode.args = []

  results = list(results_set)  

  results.sort(key=lambda term: n_nodes(term))
  return results