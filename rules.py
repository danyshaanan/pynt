
get = lambda t, l: get(t.get(l[0], {}), l[1:]) if l else t

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

rule_list = [no_not_not]