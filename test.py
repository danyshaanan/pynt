from pprint import pprint
from rules import rule_list
from main import test_rule, get_errors, get_file_errors

for rule in rule_list:
    test_rule(rule)

sample = '''
if not not (1 < 2 and  2 < a):
    f(1+1)
    pass
'''

assert len(get_errors(sample, rule_list)) == len(rule_list)

pprint(get_file_errors('rules.py', rule_list))