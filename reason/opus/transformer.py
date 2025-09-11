from reason.core import AbstractTerm

class GrammarTerm(AbstractTerm):
    pass

class Transformer:
    def transform(self, grammar_term: GrammarTerm):
        f = getattr(self, grammar_term.name)
        def mapper(x):
            if isinstance(x, GrammarTerm):
                return self.transform(x)
            else:
                return x
        return f(*map(mapper, grammar_term.args))


