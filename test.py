from pprint import pprint
from rules import rule_list
from main import test_rule, get_errors, get_path_errors

############

# path = '/Users/dany/.gh/efrontier-io/defi'
# path = '/Users/dany/.gh/efrontier-io/Futures'
path = '.'
rules = [r for r in rule_list if r.__name__ != 'no_unused']

errors = get_path_errors(path, rules)

print(f'Running rules {", ".join([rule.__name__ for rule in rules])} on path `{path}`')
for k, v in errors.items():
    print(f'\n{k}')
    print('\n'.join([f"{str(e['line']).ljust(4)}: {e['note']}" for e in v]) if v else 'No errors!')
print()
############

for rule in rule_list:
    test_rule(rule)

sample = '''
if not not (1 < 2 and  2 < a):
    f(1+1)
    pass
'''

assert len(get_errors(sample, rule_list)) == len(rule_list)

