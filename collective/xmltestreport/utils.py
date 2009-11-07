from elementtree import ElementTree

def indent(node, level=0):
    """Prepare XML for pretty-printing
    """
    
    node_indent = level * "  "
    child_indent = (level + 1) * "  "
    
    # node has childen
    if len(node):
        
        # add indent before first child node
        if not node.text or not node.text.strip():
            node.text = "\n" + child_indent
        
        # let each child indent itself
        last_idx = len(node) - 1
        for idx, child in enumerate(node):
            indent(child, level + 1)
            
            # add a tail for the next child node...
            if idx != last_idx:
                if not child.tail or not child.tail.strip():
                    child.tail = "\n" + child_indent
            # ... or for the closing element of this node
            else:
                if not child.tail or not child.tail.strip():
                    child.tail = "\n" + node_indent

def prettyXML(tree):
    """Get pretty-printed string
    """
    indent(tree)
    return ElementTree.tostring(tree)
