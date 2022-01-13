import builtins

import collections
from main import rule
from pprint import pprint

get = lambda t, l: get(t.get(l[0], {}) if type(t) == dict else next(iter(t[l[0]:l[0] + 1]), {}), l[1:]) if l else t
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
    invalid = { '1+2': [name], 'x// y': [name], 'a  * b +  c': 2 * [name], 'a+  b': [name], 'a  >>b': [name] }
    op_len = { 'FloorDiv' : 2, 'Pow' : 2, 'LShift' : 2, 'RShift' : 2, 'MatMult': 2 }
    def BinOp(self, node):
        l = space_around_binop.op_len.get(get(node, ['op', 'NAME']), 1)
        left, right = get(node, ['left']), get(node, ['right'])
        d = distance_of_nodes(left, right)
        if d - l != 2:
            self.error(node)
        else:
            node_snip = self.get_snippet(node)
            if node_snip[len(self.get_snippet(left))] != ' ' or node_snip[-1-len(self.get_snippet(right))] != ' ':
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
    valid = ['a < b', 'a < b < c', 'a < b < c < d', 'a < b or b < c', 'f(node) and f(node)']
    invalid = { 'a < b and b < c': [name], 'a < b and b < c and b < 3': [name], 'b >= a and b < c': [name], 'a < b and c > b': [name], 'a < b and x < y and b < c': [name] }
    def BoolOp(self, node):
        if get(node, ['op', 'NAME']) == 'And':
            values = [v for v in get(node, ['values']) if get(v, ['ops', 0, 'NAME']) in ['Lt', 'LtE', 'Gt', 'GtE']]
            pairs = [list((list if get(v, ['ops', 0, 'NAME']).startswith('L') else reversed)([get(v, ['left', 'id']), get(v, ['comparators', 0, 'id'])])) for v in values]
            side = lambda n: { pair[n] for pair in pairs if type(pair[n]) == str }
            if side(0).intersection(side(1)):
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
    def _For_Comprehension(self, node):
        assigned = get(node, ['target', 'id'])
        if isinstance(assigned, collections.Hashable):
            self.assigned[assigned] = node
    For = _For_Comprehension
    comprehension = _For_Comprehension
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

class duplicate_key(rule):
    name = 'DUPLICATE_KEY'
    valid = { '{"a":1,"b":2}', '{"a":1,"b":2,a:3}' }
    invalid = { '{"a":1,"b":2,"a":3}': [name] }
    def Dict(self, node):
        keys = [k['value'] for k in get(node, ['keys']) if k and k['NAME'] == 'Constant']
        if len(keys) != len(set(keys)):
            self.error(node)

class unreachable_code(rule):
    name = 'UNREACHABLE_CODE'
    valid = { 'if 1:\n  f()\n  return\ng()', 'if 1:\n  f()\n  raise\ng()' }
    invalid = { 'if 1:\n  f()\n  return\n  g()': [name], 'if 1:\n  raise\n  f()': [name] }
    def _last_statement(self, node):
        if node['parent'][-1] != node['object']:
            self.error(node)
    Return = _last_statement
    Raise = _last_statement

class _no_else_after_final_statement(rule):
    def If(self, node):
        if get(node, ['body'])[-1]['NAME'] == self.statement and 'orelse' in node and node['orelse']:
            self.error(node)

class no_else_after_return(_no_else_after_final_statement):
    name = 'NO_ELSE_AFTER_RETURN'
    valid = { 'if 1:\n  f()\nelse:\n  return', 'if a: return\nif b: return' }
    invalid = { 'if 1:\n  return\nelse:\n  pass': [name], 'if 1:\n  return\nelif 2:\n  return\nelse:\n  pass': 2 * [name] }
    def __init__(self, code, config={}):
        self.statement = 'Return'
        super().__init__(code, config)

class no_else_after_raise(_no_else_after_final_statement):
    name = 'NO_ELSE_AFTER_RAISE'
    valid = { 'if 1:\n  f()\nelse:\n  raise' }
    invalid = { 'if 1:\n  raise\nelse:\n  pass': [name], 'if 1:\n  raise\nelif 2:\n  raise\nelse:\n  pass': 2 * [name] }
    def __init__(self, code, config={}):
        self.statement = 'Raise'
        super().__init__(code, config)

class no_import_wildcard(rule):
    name = 'NO_IMPORT_WILDCARD'
    valid = { 'import a', 'from a import b', 'from a import a, b, c, d' }
    invalid = { 'from a import *': [name] }
    def ImportFrom(self, node):
        if any(n['name'] == '*' for n in get(node, ['names'])):
            self.error(node)

# class prefer_dict_comp(rule):
#     name = 'PREFER_DICT_COMP'
#     valid = { '[a for a in b]' }
#     invalid = { 'dict([(k, k) for k in a])': [name] }

class no_inconsistent_return(rule):
    name = 'NO_INCONSISTENT_RETURN'
    valid = { 'def f():\n  if 1: return 1\n  return 2', 'def f():\n  def g(): return\n  return 2' }
    invalid = { 'def f():\n  if 1:\n    return 1\n  return': [name], 'def f():\n  if 1: return 1\n  def g(): pass\n  return': [name], 'def f(a):\n  if a:\n    return\n  return True\n': [name] }
    def __init__(self, code, config={}):
        self.func_stack = []
        self.returns = { True: [], False: [] }
        super().__init__(code, config)
    def FunctionDef(self, node):
            self.func_stack.append(node)
    def FunctionDef_out(self, node):
            del node
            self.func_stack.pop()
    def Return(self, node):
        func = self.func_stack[-1]
        returns = bool(node['value'])
        if func in self.returns[not returns]:
            self.error(func)
        self.returns[returns].append(func)

class inconsistent_quotes(rule):
    name = 'INCONSISTENT_QUOTES'
    valid = { '\"a\"', '\'a\'', '\'\'\nf\"\"', 'f\'\'\n\"\"', 'f\'\'\nf\"\"', '""\nf"{\'\'}"' }
    invalid = { '\'a\'\n\"b\"': [name] }
    def __init__(self, code, config={}):
        self.quotes = set()
        self.on = True
        super().__init__(code, config)
    def JoinedStr(self, node):
        del node
        self.on = False
    def JoinedStr_out(self, node):
        del node
        self.on = True
    def Constant(self, node):
        if self.on and type(node['value']) == str:
            snippet = self.get_snippet(node)
            quotes = snippet[0]
            if quotes in '"\'':
                self.quotes.add(quotes)
                if len(self.quotes) > 1:
                    self.error(node)


################################################################################################

rule_list = [
    no_not_not,
    space_around_binop,
    space_around_boolop,
    no_abbc,
    # no_unused,
    # no_undefined,
    no_unneeded_pass,
    rule_to_test_exit_node,
    duplicate_key,
    unreachable_code,
    no_else_after_return,
    no_else_after_raise,
    no_import_wildcard,
    no_inconsistent_return,
    inconsistent_quotes,
    ]