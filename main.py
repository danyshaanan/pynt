import ast
from pathlib import Path
from pprint import pprint
from io import BytesIO
from tokenize import tokenize, COMMENT

# Requires Python 3.9
# https://docs.python.org/3/library/ast.html
# https://docs.python.org/3/library/tokenize.html

noop = lambda *a, **k: None
listify = lambda node: node.values() if type(node) == dict else node

get_code_comments = lambda s: { t.start[0]: t.string for t in tokenize(BytesIO(s.encode('utf-8')).readline) if t.type == COMMENT }
get_file_comments = lambda path: get_code_comments(open(path, 'r').read())

def get_ast_obj(code):
    def exp(n, parent=None):
        t = type(n)
        if t in { bool, int, float, str, complex, type(None), bytes }:
            return n
        if t == list:
            return [exp(i, n) for i in n]
        return { 'NAME': t.__name__, 'object': n, 'parent': parent, **{ s: exp(getattr(n, s), n) for s in n.__dict__.keys() }}
    return exp(ast.parse(code, type_comments=True))

def traverse(node, cb_in, cb_out):
    if type(node) in { list, dict }:
        cb_in(node)
        [traverse(v, cb_in, cb_out) for v in listify(node)]
        cb_out(node)

def get_code_errors(code, rules):
    instances = [rule(code, rule.config) for rule in rules]
    visitor = lambda suffix: lambda node: [getattr(instance, node['NAME'] + suffix, noop)(node) for instance in instances] if 'NAME' in node else 0
    traverse(get_ast_obj(code), visitor(''), visitor('_out'))
    return [instance.get_errors() for instance in instances]

def get_file_errors(path, rules):
    return get_code_errors(open(path, 'r').read(), rules)

def get_path_errors(path, rules):
    res = {}
    files = Path(path).rglob('*.py')
    for file in files:
        errors = get_file_errors(file, rules)
        errors = [item for sublist in errors for item in sublist]
        errors = sorted(errors, key = lambda e: e['line'])
        res[file] = errors
    return res

def print_errors(errors):
    for k, v in errors.items():
        print(f'\n{k}')
        print('\n'.join([f"{str(e['line']).ljust(4)}: {e['note'].ljust(25)} : {e['snippet'].strip()}" for e in v]) if v else 'No errors!')
    print()

class rule():
    testing = False
    config = {}
    def __init__(self, code, config={}):
        self.code = code
        self.errors = []
    def get_snippet(self, node):
        line_start, line_end = node['lineno'], node['end_lineno']
        col_start, col_end = node['col_offset'], node['end_col_offset']
        if line_start != line_end:
            return 'MULTI_LINE'
        return self.code.split('\n')[line_start - 1][col_start:col_end]
    def error(self, node):
        self.errors.append({ 'note': self.name, 'line': node['lineno'], 'snippet': self.get_snippet(node) })
    def get_errors(self):
        return self.errors

def test_rule(rule):
    print(f'Testing rule {rule}...')
    for case, expected in [(k, []) for k in rule.valid] + list(rule.invalid.items()):
        # if rule.testing:
        actual = [e['note'] for e in get_code_errors(case, [rule])[0]]
        assert actual == expected, f'(actual != expected): ({actual} != {expected}) for case `{case}`'

    # for case, expected in [(k, []) for k in rule.valid]:
    #     # if rule.testing:
    #     actual = [e['note'] for e in get_code_errors(case, [rule])[0]]
    #     assert actual == expected, f'(actual != expected): ({actual} != {expected}) for case `{case}`'

    # for case, expected in list(rule.invalid.items()):
    #     # if rule.testing:
    #     actual = [e['note'] for e in get_code_errors(case, [rule])[0]]
    #     assert actual == expected, f'(actual != expected): ({actual} != {expected}) for case `{case}`'

if __name__ == '__main__':
    from pprint import pprint
    code = 'not not 1j'
    pprint(get_ast_obj(code))


    