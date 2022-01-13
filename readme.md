
## TODO:
* Proper scope handling
* Implement configurations
* Implement disable comments
* Decide on proper rule format and then rule testing format
* feature - include file name in rule logic - reconsider, might complicate lots of things
* Error handling (on failing on parsing mainly)
* Add critical rules:
    * fix no unused / not assigned
    * go over pylint list
    * go over eslint rules
    * ...



## To figure out:
* What is the concise yet effective rule testing format?
* How should the testing api actually look / how does it affects the representation? Rethink the representation. Maybe should not recreated, but wrap original in helper functions
* What's missing in terms of parenthood/ancestorhood / scoping?
