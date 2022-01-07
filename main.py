import ast
from pprint import pprint

# Requires Python 3.9
# https://docs.python.org/3/library/ast.html

noop = lambda *a, **k: None

def get_ast_obj(code):
    def exp(n):
        t = type(n)
        if t in { bool, int, float, str, complex, type(None) }:
            return n
        if t == list:
            return [exp(i) for i in n]
        return { 'name': t.__name__, **{ s: exp(getattr(n, s)) for s in n.__dict__.keys() }}
    return exp(ast.parse(code))

def traverse(tree, cb):
    stack = [tree]
    while stack:
        i = stack.pop(0)
        if type(i) in { dict, list }:
            o = i if type(i) == dict else dict(enumerate(i))
            [cb(k, o[k], o) if k == 'name' else stack.append(o[k]) for k in o]

def get_errors(code, rule):
    instance = rule(rule.config)
    visit = lambda _, __, node: getattr(instance, node['name'], noop)(node)
    traverse(get_ast_obj(code), visit)
    return instance.get_errors()

class rule():
    testing = False
    config = {}
    def __init__(self, config={}):
        self.errors = []
    def error(self, e):
        self.errors.append(e)
    def get_errors(self):
        return self.errors

def test_rule(rule):
    print(f'Testing rule {rule}...')
    for case, expected in [(k, []) for k in rule.valid] + list(rule.invalid.items()):
        # if rule.testing:
        actual = get_errors(case, rule)
        assert actual == expected, f'(actual != expected): ({actual} != {expected}) for case `{case}`'

if __name__ == '__main__':
    from pprint import pprint
    code = 'not not 1j'
    pprint(get_ast_obj(code, verbose=True))
    pprint(get_ast_obj(code))

