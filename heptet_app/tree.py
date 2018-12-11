from zope.interface import Interface, implementer

class ITree(Interface):
    pass
    

class TreeNode:
    def __init__(self, name, children=None):
        self._name = name
        self._children = children or []

    @property
    def children(self) -> 'MutableSequence':
        return self._children

    def __repr__(self):
        return "TreeNode(%r, %r)" % (self._name, self._children)

    
@implementer(ITree)
class Tree:
    def __init__(self, name):
        self._name = name
        self._root = TreeNode("root")

    @property
    def root(self) -> TreeNode:
        return self._root

    def __repr__(self):
        return "Tree(%r, %r)" % (self._name, self._root)

def config_directive_register_tree(config, name=''):
    tree = Tree(name)
    config.registry.registerUtility(tree, ITree, name)
    return tree

def config_directive_get_tree(config, name=''):
    return config.registry.getUtility(ITree, name)

def config_directive_tree_add_resource(config, tree_or_name, resource):
    if isinstance(tree_or_name, str):
        tree = config_directive_get_tree(config, tree_or_name)
    else:
        tree = tree_or_name

    tree.root.children.append(resource)
    

def includeme(config):
    config.add_directive('register_tree', config_directive_register_tree)
    config.add_directive('get_tree', config_directive_get_tree)
    config.add_directive('tree_add_resource', config_directive_tree_add_resource)
