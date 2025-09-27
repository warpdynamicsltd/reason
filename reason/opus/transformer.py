import traceback

from reason.core import AbstractTerm

class GrammarTerm(AbstractTerm):
    pass

class Transformer:
    def _list(self, *args):
        return args

    @staticmethod
    def vargs(func):
        def wrapper(self, args):
           return func(self, *args)

        return wrapper

    def transform(self, grammar_term: GrammarTerm):
        if hasattr(self, grammar_term.name):
            if hasattr(grammar_term, "transform"):
                f = getattr(grammar_term, "transform")
            else:
                f = getattr(self, grammar_term.name)
        else:
            f = lambda x: x

        def mapper(x):
            if isinstance(x, GrammarTerm):
                return self.transform(x)
            else:
                return x
        try:
            return f(*map(mapper, grammar_term.args))
        except Exception as e:
            print("Stopped on:")
            print(grammar_term)
            traceback.print_exc()
            # raise e


