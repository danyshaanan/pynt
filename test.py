from rules import rule_list
from main import get_ast_obj, test_rule

tests = [{
    'input': '1',
    'output': {'NAME': 'Module', 'type_ignores': [], 'body': [{'NAME': 'Expr', 'col_offset': 0, 'end_col_offset': 1, 'lineno': 1, 'end_lineno': 1, 'value': {'NAME': 'Constant', 'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 1, 'lineno': 1, 'kind': None, 'value': 1}}]}
}, {
    'input': 'a',
    'output': {'NAME': 'Module', 'body': [{'NAME': 'Expr', 'value': {'NAME': 'Name', 'id': 'a', 'ctx': {'NAME': 'Load'}, 'lineno': 1, 'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 1}, 'lineno': 1, 'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 1}], 'type_ignores': []}
}]

for test in tests:
    assert get_ast_obj(test['input']) == test['output'], get_ast_obj(test['input'])

for rule in rule_list:
    test_rule(rule)

