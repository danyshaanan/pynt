
get = lambda t, l: get(t.get(l[0], {}), l[1:]) if l else t
distance_of_nodes = lambda n1, n2: get(n2, ['col_offset']) - get(n1, ['end_col_offset'])

class no_not_not():
    str = 'Cast to boolean with `bool()`, not with `not not`'
    valid = { 'not 1', 'not NOT', 'not False', }
    invalid = { 'not not 1': [str], 'not not not 1': 2 * [str] }
    is_not = lambda node: get(node, ['op','name']) == 'Not'
    def __init__(self):
        self.errors = []
    def UnaryOp(self, node):
        if no_not_not.is_not(node) and no_not_not.is_not(node['operand']):
            self.errors.append(no_not_not.str)

class space_around_binop():
    str = 'Put spaces around binary operators: use `1 + 2` instead of `1+2`'
    valid = [f'x {o} y' for o in '+ - * / // ** << >> | & ^'.split(' ')] + ['asd - sad', 'a * b * c']
    invalid = { '1+2': [str], 'x// y': [str], 'a  * b +  c': 2 * [str] }
    op_len = { 'FloorDiv' : 2, 'Pow' : 2, 'LShift' : 2, 'RShift' : 2, 'MatMult': 2 }
    def __init__(self):
        self.errors = []
    def BinOp(self, node):
        l = space_around_binop.op_len.get(get(node, ['op', 'name']), 1)
        d = distance_of_nodes(get(node, ['left']), get(node, ['right']))
        if d - l != 2:
            self.errors.append(space_around_binop.str)


class space_around_boolop():
    str = 'Put spaces around binary operators: use `a and b` instead of `a   and    b`'
    valid = ['a and b', 'a or b', 'a and b or c']
    invalid = { 'a  and  b': [str], 'x  or y': [str], 'a  and b or  c': 2 * [str] }
    op_len = { 'Or': 2, 'And':  3 }
    def __init__(self):
        self.errors = []
    def BoolOp(self, node):
        l = len(get(node, ['op', 'name']))
        args = get(node, ['values'])
        for i in range(len(args) - 1):
            d = distance_of_nodes(args[i], args[i + 1])
            if d - l != 2:
                self.errors.append(space_around_boolop.str)

rule_list = [
    no_not_not,
    space_around_binop,
    space_around_boolop,
    ]