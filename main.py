import ast

# Requires Python 3.9
# https://docs.python.org/3/library/ast.html

def get_ast_obj(code, verbose=False):
    filterout = set() if verbose else { 'lineno', 'end_lineno', 'col_offset', 'end_col_offset' }
    def exp(n):
        t = type(n)
        if t in { bool, int, float, str, complex, type(None) }:
            return n
        if t == list:
            return [exp(i) for i in n]
        return { 'name': t.__name__, **{ s: exp(getattr(n, s)) for s in set(n.__dict__.keys()) - filterout }}
    return exp(ast.parse(code))

if __name__ == '__main__':
    from pprint import pprint
    code = 'not not 1j'
    pprint(get_ast_obj(code, verbose=True))
    pprint(get_ast_obj(code))

