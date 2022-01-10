import builtins

import collections
from main import rule
from pprint import pprint

get = lambda t, l: get(t.get(l[0], {}) if type(t) == dict else next(iter(t[l[0]:l[0]+1]), {}), l[1:]) if l else t
distance_of_nodes = lambda n1, n2: get(n2, ['col_offset']) - get(n1, ['end_col_offset'])

class no_not_not(rule):
    name = 'NO_NOT_NOT'
    hint = 'Cast to boolean with `bool()`, not with `not not`'
    valid = { 'not 1', 'not NOT', 'not False', }
    invalid = { 'not not 1': [name], 'not not not 1': 2 * [name] }
    is_not = lambda node: get(node, ['op','NAME']) == 'Not'
    def UnaryOp(self, node):
        if no_not_not.is_not(node) and no_not_not.is_not(node['operand']):
            self.error(node)

class space_around_binop(rule):
    name = 'SPACE_AROUND_BINOP'
    str = 'Put spaces around binary operators: use `1 + 2` instead of `1+2`'
    valid = [f'x {o} y' for o in '+ - * / // ** << >> | & ^ @='.split(' ')] + ['asd - sad', 'a * b * c']
    invalid = { '1+2': [name], 'x// y': [name], 'a  * b +  c': 2 * [name] } # , 'a+  b': [str]
    op_len = { 'FloorDiv' : 2, 'Pow' : 2, 'LShift' : 2, 'RShift' : 2, 'MatMult': 2 }
    def BinOp(self, node):
        l = space_around_binop.op_len.get(get(node, ['op', 'NAME']), 1)
        d = distance_of_nodes(get(node, ['left']), get(node, ['right']))
        if d - l != 2:
            self.error(node)


class space_around_boolop(rule):
    name = 'SPACE_AROUND_BOOLOP'
    str = 'Put spaces around binary operators: use `a and b` instead of `a   and    b`'
    valid = ['a and b', 'a or b', 'a and b or c']
    invalid = { 'a  and  b': [name], 'x  or y': [name], 'a  and b or  c': 2 * [name] }
    op_len = { 'Or': 2, 'And':  3 }
    def BoolOp(self, node):
        l = len(get(node, ['op', 'NAME']))
        args = get(node, ['values'])
        for i in range(len(args) - 1):
            d = distance_of_nodes(args[i], args[i + 1])
            if d - l != 2:
                self.error(node)

class no_abbc(rule):
    name = 'NO_ABBC'
    valid = ['a < b', 'a < b < c', 'a < b < c < d', 'a < b or b < c']
    # valid = ['a < b', 'a < b < c', 'a < b < c < d', 'a < b or b < c', 'a < b and b > c']
    invalid = { 'a < b and b < c': [name], 'a < b and b < c and b < 3': [name] }
    # invalid = { 'a < b and b < c': [str], 'a < b and b < c and b < 3': [str], 'a < b and c > b': [str] }
    def __init__(self, code, config={}):
        # self.str = 'ASDASDASDAS'
        # self.hint = 'Do not use `a < b and b < c`. Use `a < b < c` instead.'
        # self.valid = ['a < b', 'a < b < c', 'a < b < c < d', 'a < b or b < c']
        # self.invliad = { 'a < b and b < c': [self.str], 'a < b and b < c and b < 3': [self.str] }
        super().__init__(code, config)
    def BoolOp(self, node):
        if get(node, ['op', 'NAME']) == 'And':
            values = get(node, ['values'])
            if values:
                for i in range(len(values) - 1):
                    if get(values[i], ['comparators', 0, 'id']) == get(values[i + 1], ['left', 'id']):
                        self.error(node)

class no_unused_no_undefined(rule): # TODO: Fix, should look inside context and not in all code
    def __init__(self, code, config={}):
        super().__init__(code, config)
        self.assigned = {}
        self.used = {}
        self.globals = set(config.get('globals', []))
    def Assign(self, node):
        for target in get(node, ['targets']):
            assigned = get(target, ['id'])
            if isinstance(assigned, collections.Hashable):
                self.assigned[assigned] = node
    def FunctionDef(self, node):
        assigned = get(node, ['name'])
        self.assigned[assigned] = node
    def Import(self, node):
        for n in get(node, ['names']):
            self.assigned[n['name']] = node
    def ImportFrom(self, node):
        for n in get(node, ['names']):
            self.assigned[n['name']] = node
    def _For_Cmprehension(self, node):
        assigned = get(node, ['target', 'id'])
        if isinstance(assigned, collections.Hashable):
            self.assigned[assigned] = node
    def For(self, node):
        return self._For_Cmprehension(node)
    def comprehension(self, node):
        return self._For_Cmprehension(node)
    ###
    def Expr(self, node):
        for target in get(node, ['value', 'args']):
            id = get(target, ['id'])
            if id:
                self.used[id] = node
    def Call(self, node):
        called = get(node, ['func', 'id'])
        if isinstance(called, collections.Hashable):
            self.used[called] = node
    # def Name(self, node):
    #     self.used[get(node, ['id'])] = node
    # TODO: Add other usages beside Assign and Expr

class no_unused(no_unused_no_undefined):
    name = 'NO_UNUSED'
    valid = ['a = 3\nprint(a)', 'def f():f()']
    invalid = { 'a = 3': [name], 'def f():pass': [name], 'import a': [name], 'from a import b': [name] }
    def get_errors(self):
        for v, node in self.assigned.items():
            if v not in self.used:
                self.error(node)
        return super().get_errors()

class no_undefined(no_unused_no_undefined):
    name = 'NO_UNDEFINED'
    valid = ['a = 3\nprint(a)', 'def f():f()', 'from a import b', 'for i in []: print(i)', '[rule() for rule in []]']
    invalid = { 'print(a)': [name], 'f(1)': [name] }
    config = { 'globals': dir(builtins) }
    def get_errors(self):
        for v, node in self.used.items():
            if not (v in self.assigned or v in self.globals):
                self.error(node)
        return super().get_errors()

class no_unneeded_pass(rule):
    name = 'NO_UNNEEDED_PASS'
    hint = 'do not use `pass` if not needed'
    valid = { 'if 1:\n  pass' }
    invalid = { f'{c}:\n  3\n  pass': ['NO_UNNEEDED_PASS'] for c in ['if 1', 'def f()', 'while a', 'for i in a', 'with a'] }
    def Pass(self, node):
        body = get(node, ['parent'])
        if len(body) >= 2 and body[-1] == node['object']:
            self.error(node)

class rule_to_test_exit_node(rule):
    # let's do: no pass inside if
    name = 'TEST_EXIT'
    valid = { 'if 1: 3\nwhile 1:pass' }
    invalid = { 'if 1: pass\nwhile1: 3': [name] }
    def __init__(self, code, config={}):
        self.if_counter = 0
        super().__init__(code, config)
    def If(self, node):
        self.if_counter += 1
    def If_out(self, node):
        self.if_counter -= 1
    def Pass(self, node):
        if self.if_counter:
            self.error(node)

rule_list = [
    no_not_not,
    space_around_binop,
    space_around_boolop,
    no_abbc,
    # no_unused,
    # no_undefined,
    no_unneeded_pass,
    rule_to_test_exit_node,
    ]