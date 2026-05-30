

def traverse(root):
    if hasattr(root, "PlumeID"):
        yield root
    if hasattr(root, "Group"):
        for obj in root.Group:
            if hasattr(obj, "LinkedObject"):
                obj = obj.LinkedObject
            yield from traverse(obj)
