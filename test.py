from pprint import pprint
from rules import rule_list
from main import test_rule, get_code_errors, get_path_errors, print_errors, get_code_comments, get_file_comments

############

for code, comments in {
    'a = 3': {},
    '#todo': { 1: '#todo' },
    '#todo #todo': { 1: '#todo #todo' },
    '#a\n#b\n#': { 1: '#a', 2: '#b', 3: '#' },
    '\n\n\n\n\n\n\n#': { 8: '#' },
}.items():
    assert get_code_comments(code) == comments, f'Code `{code}` does not produce comments {comments} (should be {get_code_comments(code)})'


# path = '/Users/dany/.gh/efrontier-io/defi'
# path = '/Users/dany/.gh/efrontier-io/Futures'
path = '.'
rules = [r for r in rule_list if r.__name__ != 'no_unused']

print(f'Running rules {", ".join([rule.__name__ for rule in rules])} on path `{path}`')
print_errors(get_path_errors(path, rules))

pprint(get_file_comments('main.py'))
print()

############

for rule in rule_list:
    test_rule(rule)

sample = '''
if not not (1 < 2 and  2 < a):
    f(1+1)
    pass
'''

assert len(get_code_errors(sample, rule_list)) == len(rule_list)
