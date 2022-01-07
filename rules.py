from main import rule
from pprint import pprint

get = lambda t, l: get(t.get(l[0], {}) if type(t) == dict else next(iter(t[l[0]:l[0]+1]), {}), l[1:]) if l else t
distance_of_nodes = lambda n1, n2: get(n2, ['col_offset']) - get(n1, ['end_col_offset'])

class no_not_not(rule):
    str = 'Cast to boolean with `bool()`, not with `not not`'
    valid = { 'not 1', 'not NOT', 'not False', }
    invalid = { 'not not 1': [str], 'not not not 1': 2 * [str] }
    is_not = lambda node: get(node, ['op','name']) == 'Not'
    def UnaryOp(self, node):
        if no_not_not.is_not(node) and no_not_not.is_not(node['operand']):
            self.error(no_not_not.str)

class space_around_binop(rule):
    str = 'Put spaces around binary operators: use `1 + 2` instead of `1+2`'
    valid = [f'x {o} y' for o in '+ - * / // ** << >> | & ^'.split(' ')] + ['asd - sad', 'a * b * c']
    invalid = { '1+2': [str], 'x// y': [str], 'a  * b +  c': 2 * [str] }
    op_len = { 'FloorDiv' : 2, 'Pow' : 2, 'LShift' : 2, 'RShift' : 2, 'MatMult': 2 }
    def BinOp(self, node):
        l = space_around_binop.op_len.get(get(node, ['op', 'name']), 1)
        d = distance_of_nodes(get(node, ['left']), get(node, ['right']))
        if d - l != 2:
            self.error(space_around_binop.str)


class space_around_boolop(rule):
    str = 'Put spaces around binary operators: use `a and b` instead of `a   and    b`'
    valid = ['a and b', 'a or b', 'a and b or c']
    invalid = { 'a  and  b': [str], 'x  or y': [str], 'a  and b or  c': 2 * [str] }
    op_len = { 'Or': 2, 'And':  3 }
    def BoolOp(self, node):
        l = len(get(node, ['op', 'name']))
        args = get(node, ['values'])
        for i in range(len(args) - 1):
            d = distance_of_nodes(args[i], args[i + 1])
            if d - l != 2:
                self.error(space_around_boolop.str)

class no_abbc(rule):
    str = 'Do not use `a < b and b < c`. Use `a < b < c` instead.'
    valid = ['a < b', 'a < b < c', 'a < b < c < d', 'a < b or b < c']
    # valid = ['a < b', 'a < b < c', 'a < b < c < d', 'a < b or b < c', 'a < b and b > c']
    invalid = { 'a < b and b < c': [str], 'a < b and b < c and b < 3': [str] }
    # invalid = { 'a < b and b < c': [str], 'a < b and b < c and b < 3': [str], 'a < b and c > b': [str] }
    def BoolOp(self, node):
        if get(node, ['op', 'name']) == 'And':
            values = get(node, ['values'])
            if values:
                for i in range(len(values) - 1):
                    if get(values[i], ['comparators', 0, 'id']) == get(values[i + 1], ['left', 'id']):
                        self.error(no_abbc.str)

class no_unused(rule): # TODO: Fix, should look inside context and not in all code
    str = 'NO UNUSED / NOT DEFINED'
    valid = ['a = 3\na(a)', 'f = 3\nf(1)']
    invalid = { 'a = 3': [str], 'print(a)': [str], 'a=3\nf(a)': [str] }
    config = { 'globals': ['print'] }
    def __init__(self, config={}):
        super().__init__()
        self.assigned = set()
        self.used = set()
        self.globals = set(config.get('globals', []))
    def Assign(self, node):
        for target in get(node, ['targets']):
            self.assigned.add(get(target, ['id']))
    def Expr(self, node):
        for target in get(node, ['value', 'args']):
            id = get(target, ['id'])
            if id:
                self.used.add(id)
    def Call(self, node):
        self.used.add(get(node, ['func', 'id']))
    # TODO: Add other usages beside Assign and Expr
    def get_errors(self):
        return [no_unused.str for _ in (self.assigned - self.used) | (self.used - self.assigned - self.globals)]


rule_list = [
    no_not_not,
    space_around_binop,
    space_around_boolop,
    no_abbc,
    no_unused,
    ]