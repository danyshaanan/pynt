

## Updates:

* Fix `name` override (which broke `no_unneeded_pass` implementation)
* Implement parenthood (So that `no_unneeded_pass` could be properly written)
* Implement multi-visitor (One traversal for many rules)
* Implement getting errors per file (read file and pass as code)
* Add line numbers for errors (and printed sorted output)
* Fix all rules error till it runs on futures

## TODO:
* Add violating code snippet to error
* feature - include file name in rule logic - reconsider, might complicate lots of things
* Error handling (on failing on parsing mainly)
* Implement configurations
* Add critical rules:
    * fix no unused / not assigned
    * go over pylint list
    * go over eslint rules
    * ...
