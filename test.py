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
}, {
    'input': 'for i in l: pass',
    'output': {'name': 'Module', 'type_ignores': [], 'body': [{'name': 'For', 'type_comment': None, 'body': [{'name': 'Pass'}], 'target': {'name': 'Name', 'id': 'i', 'ctx': {'name': 'Store'}}, 'iter': {'name': 'Name', 'id': 'l', 'ctx': {'name': 'Load'}}, 'orelse': []}]}
}]

vtests = [{
    'input': '1',
    'output': {'name': 'Module', 'type_ignores': [], 'body': [{'name': 'Expr', 'col_offset': 0, 'end_col_offset': 1, 'lineno': 1, 'end_lineno': 1, 'value': {'name': 'Constant', 'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 1, 'lineno': 1, 'kind': None, 'value': 1}}]}
}]

for test in tests:
    assert get_ast_obj(test['input']) == test['output'], get_ast_obj(test['input'])

for test in vtests:
    assert get_ast_obj(test['input'], verbose=True) == test['output'], get_ast_obj(test['input'], verbose=True)
