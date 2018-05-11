"""
Replace everything to accomodate the typesetters
"""

from panflute import *

def action(elem, doc):
    if isinstance(elem, Para) and isinstance(elem.next, BulletList):
        return elem
    if isinstance(elem, Para) and isinstance(elem.next, Header):
        return elem
    if isinstance(elem, Para) and isinstance(elem.next, Note):
        pass
    if isinstance(elem, Para) and elem.next == None:
        pass
    if isinstance(elem, Para) and elem.prev == None:
        pass
    if isinstance(elem, Para):
        e = Para(Str(''))
        return [elem, e]
    if isinstance(elem, Header):
        e = Para(Str(''))
        return [e, e, elem]
        

def main(doc=None):
    return run_filter(action, doc=doc) 

if __name__ == '__main__':
    main()