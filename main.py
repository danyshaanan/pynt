import ast
from pprint import pprint

# Requires Python 3.9
# https://docs.python.org/3/library/ast.html

noop = lambda *a, **k: None

def get_ast_obj(code):
    def exp(n, parent=None):
        t = type(n)
        if t in { bool, int, float, str, complex, type(None) }:
            return n
        if t == list:
            return [exp(i, n) for i in n]
        return { 'NAME': t.__name__, 'object': n, 'parent': parent, **{ s: exp(getattr(n, s), n) for s in n.__dict__.keys() }}
    return exp(ast.parse(code))

def traverse(tree, cb):
    stack = [tree]
    while stack:
        i = stack.pop(0)
        if type(i) in { dict, list }:
            o = i if type(i) == dict else dict(enumerate(i))
            [cb(k, o[k], o) if k == 'NAME' else stack.append(o[k]) for k in o]

def get_errors(code, rules):
    instances = [rule(rule.config) for rule in rules]
    visit = lambda _, __, node: [getattr(instance, node['NAME'], noop)(node) for instance in instances]
    traverse(get_ast_obj(code), visit)
    return [instance.get_errors() for instance in instances]

def get_file_errors(path, rules):
    return get_errors(open(path, 'r').read(), rules)

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
        actual = get_errors(case, [rule])[0]
        assert actual == expected, f'(actual != expected): ({actual} != {expected}) for case `{case}`'

if __name__ == '__main__':
    from pprint import pprint
    code = 'not not 1j'
    pprint(get_ast_obj(code))

    