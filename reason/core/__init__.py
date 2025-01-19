class AbstractTerm:
  def __init__(self, name, *args):
    self.name = name
    self.args = args

  def __hash__(self):
    if not self.args:
      return hash((type(self), self.name))
    else:
      return hash((type(self), self.name, *self.args))
    
  def __eq__(self, other):
    return type(self) == type(other) and self.name == other.name and self.args == other.args
  
  def replace(self, source, target):
    new_args = []
    for arg in self.args:
      if arg == source:
        new_arg = target
      elif isinstance(arg, AbstractTerm):
        new_arg = arg.replace(source, target)
      else:
        new_arg = arg

      new_args.append(new_arg)

    return type(self)(self.name, *new_args)
  
  def show(self):
    if self.args:
      return f"{type(self).__name__}({self.name}, {', '.join(map(AbstractTerm.show, self.args))})"
    else:
      return f"{type(self).__name__}({self.name})"
  
  # def __repr__(self):
  #   if self.args:
  #     return f"{type(self).__name__}({self.name}, {', '.join(map(repr, self.args))})"
  #   else:
  #     return f"{type(self).__name__}({self.name})"
  
  def __repr__(self):
    if self.args:
      return f"{self.name}({', '.join(map(repr, self.args))})"
    else:
      return f"{self.name}"

class Variable(AbstractTerm):
  pass

class Const(AbstractTerm):
  pass