
not not no_not_not

space_around_binop+space_around_binop

space_around_boolop  and    space_around_boolop

0 < no_abbc and no_abbc < 1

no_unused = no_undefined

def no_unneeded_pass():
    print(1)
    pass

duplicate_key = { 'a': 1, 'b': 2, 'a': 3 }

def unreachable_code():
    return
    if 1:
        return
        while True:
            return
            raise
            unreachable_code()

def no_else_after_return():
    if 1:
        return
    else:
        pass

if no_else_after_raise:
    raise
else:
    1

from a import *

def no_inconsistent_return(a):
    if a:
        return
    return True


b = "123"
C = 'asd'