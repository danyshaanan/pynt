import ast
from pathlib import Path
from pprint import pprint

# Requires Python 3.9
# https://docs.python.org/3/library/ast.html

noop = lambda *a, **k: None

def get_ast_obj(code):
    def exp(n, parent=None):
        t = type(n)
        if t in { bool, int, float, str, complex, type(None), bytes }:
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
            [cb(o) if k == 'NAME' else stack.append(o[k]) for k in o]

def get_code_errors(code, rules):
    instances = [rule(code, rule.config) for rule in rules]
    visit = lambda node: [getattr(instance, node['NAME'], noop)(node) for instance in instances]
    traverse(get_ast_obj(code), visit)
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

    