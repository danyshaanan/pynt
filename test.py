from main import get_ast_obj

tests = [{
    'input': 'a',
    'output': {'name': 'Module', 'body': [{'name': 'Expr', 'value': {'name': 'Name', 'id': 'a', 'ctx': {'name': 'Load'}}}], 'type_ignores': []}
}, {
    'input': 'True',
    'output': {'name': 'Module', 'type_ignores': [], 'body': [{'name': 'Expr', 'value': {'name': 'Constant', 'value': True, 'kind': None}}]}
}, {
    'input': '1+.2',
    'output': {'name': 'Module', 'body': [{'name': 'Expr', 'value': {'name': 'BinOp', 'op': {'name': 'Add'}, 'right': {'name': 'Constant', 'value': 0.2, 'kind': None}, 'left': {'name': 'Constant', 'value': 1, 'kind': None}}}], 'type_ignores': []}
}]

for test in tests:
    assert get_ast_obj(test['input']) == test['output'], get_ast_obj(test['input'])

vtests = [{
    'input': '1',
    'output': {'name': 'Module', 'type_ignores': [], 'body': [{'name': 'Expr', 'col_offset': 0, 'end_col_offset': 1, 'lineno': 1, 'end_lineno': 1, 'value': {'name': 'Constant', 'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 1, 'lineno': 1, 'kind': None, 'value': 1}}]}
}]

for test in vtests:
    assert get_ast_obj(test['input'], verbose=True) == test['output'], get_ast_obj(test['input'], verbose=True)

from rules import rule_list
from main import test_rule

for rule in rule_list:
    test_rule(rule)

