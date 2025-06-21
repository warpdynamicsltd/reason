import reason
from lark import v_args


def v_args_return_with_meta(method):
    def modified_method(self, meta, children):
        res = method(self, *children)
        if isinstance(res, reason.parser.tree.AbstractSyntaxTree):
            setattr(res, "meta", meta)
        return res

    return v_args(meta=True)(modified_method)

def v_args_with_meta_return_with_meta(method):
    def modified_method(self, meta, children):
        res = method(self, meta, *children)
        if isinstance(res, reason.parser.tree.AbstractSyntaxTree):
            setattr(res, "meta", meta)
        return res

    return v_args(meta=True)(modified_method)
