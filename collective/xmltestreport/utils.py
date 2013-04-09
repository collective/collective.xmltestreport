try:
    # Python >= 2.5
    from xml.etree import ElementTree
except ImportError:
    # Python < 2.5
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

#XXX Ugly monkey patch to get it at least working,
# better ulgy output than no output


def patched_write_encoded(fname, text, encoding='utf8', errors='strict'):
    '''Write utf8 string `text` to file names `fname`, with encoding.'''
    import codecs
    f = codecs.open(fname, 'w', encoding=encoding, errors=errors)
    try:
        f.write(text.decode('utf8'))
    except UnicodeDecodeError:
        print "UnicodeDecodeError in file (%s)" % fname
        f = codecs.open(fname, 'w', errors=errors)
        f.write(text)
    finally:
        f.close()


def write_html(self, fname, html):
    """Write `html` to `fname`, properly encoded."""
    patched_write_encoded(fname, html, 'ascii', 'xmlcharrefreplace')

import coverage.html
coverage.html.HtmlReporter.write_html = write_html


def _escape_cdata(text, encoding):
    # escape character data
    try:
        # it's worth avoiding do-nothing calls for strings that are
        # shorter than 500 character, or so.  assume that's, by far,
        # the most common case in most applications.
        if "&" in text:
            text = text.replace("&", "&amp;")
        if "<" in text:
            text = text.replace("<", "&lt;")
        if ">" in text:
            text = text.replace(">", "&gt;")
        return text.encode(encoding, "xmlcharrefreplace")
    except (TypeError, AttributeError):
        ElementTree._raise_serialization_error(text)
    #XXX this is the patch
    except (UnicodeDecodeError):
        return text.decode("utf-8").encode(encoding, "xmlcharrefreplace")

ElementTree._escape_cdata = _escape_cdata
