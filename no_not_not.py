from pprint import pprint

noop = lambda *a, **k: None

g = lambda t, l: g(t.get(l[0], {}), l[1:]) if l else t

# is_not = lambda node: node['op']['name'] == 'Not'
is_not = lambda node: g(node, ['op','name']) == 'Not'

class no_not_not():
    def __init__(self):
        self.errors = []
    def UnaryOp(self, node):
        print('isnot', node, is_not(node))
        if is_not(node) and is_not(node['operand']):
            self.errors.append('Do not use not not, use `bool()`')
        # self.errors.append('test error: no not not')



a = {'name': 'Module', 'type_ignores': [], 'body': [{'name': 'Expr', 'value': {'name': 'BinOp', 'op': {'name': 'Add'}, 'left': {'name': 'Constant', 'value': 2, 'kind': None}, 'right': {'name': 'Constant', 'value': 2, 'kind': None}}}]}

from main import get_ast_obj

def traverse(tree, cb):
    stack = [tree]
    while stack:
        i = stack.pop(0)
        if type(i) in { dict, list }:
            o = i if type(i) == dict else dict(enumerate(i))
            [cb(k, o[k], o) if k == 'name' else stack.append(o[k]) for k in o]

print(a)
traverse(a, print)
print('---')
b = get_ast_obj('not "1"')
print(b)
traverse(b, print)


def get_errors(code, rule):
    instance = rule()
    tree = get_ast_obj(code)
    pprint(tree)

    visit = lambda _, __, node: getattr(instance, node['name'], noop)(node)
    traverse(tree, visit)
    print(instance.errors)


get_errors('not not 1', no_not_not)

