import reason
from lark import v_args


def v_args_return_with_meta(method):
    def modified_method(self, meta, children):
        # print(meta.__dict__)
        res = method(self, *children)
        if isinstance(res, reason.parser.tree.AbstractSyntaxTree):
            setattr(res, "meta", meta)
        return res

    return v_args(meta=True)(modified_method)
