def _pretty(element):
    retval = []
    for child in element.getchildren():
        tag = child.tag.split("}")[1]
        retval.append("<")
        retval.append(tag)
        retval.extend([' %s="%s"' % (key, child.attrib[key]) for key in child.keys()])
        retval.append(">")
        if child.text:
            retval.append(child.text)
        retval.extend(_pretty(child))
        retval.append("</%s>" % tag) 
        if child.tail:
            retval.append(child.tail)
    return retval


def pretty(element):
    return "".join(_pretty(element))
