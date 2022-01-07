import ast

# Requires Python 3.9
# https://docs.python.org/3/library/ast.html

noop = lambda *a, **k: None

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

def traverse(tree, cb):
    stack = [tree]
    while stack:
        i = stack.pop(0)
        if type(i) in { dict, list }:
            o = i if type(i) == dict else dict(enumerate(i))
            [cb(k, o[k], o) if k == 'name' else stack.append(o[k]) for k in o]

def get_errors(code, rule):
    instance = rule()
    tree = get_ast_obj(code)
    visit = lambda _, __, node: getattr(instance, node['name'], noop)(node)
    traverse(tree, visit)
    return instance.errors

def test_rule(rule):
    print(f'Testing rule {rule}...')
    for case in rule.valid:
        assert get_errors(case, rule) == []
    for case in rule.invalid:
        assert get_errors(case, rule)

if __name__ == '__main__':
    from pprint import pprint
    code = 'not not 1j'
    pprint(get_ast_obj(code, verbose=True))
    pprint(get_ast_obj(code))

