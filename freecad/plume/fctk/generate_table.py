from collections import defaultdict
import FreeCAD as App
import FreeCADGui as Gui

from itertools import groupby
from collections import defaultdict

from .utils import *



def make_table(grouped_objects, attributes, funcs={}):
    """

    return a data list in a form of [row1, row2] with rows = (c0, c1, ...)
    
    It checks if attributes exists for the link, then for the obj
    It will join the set of data by default, so in a group, IDs will give "1,2,3" if differents, or "2" if same (not "2,2,2)

    the #attribute will apply a function from func.
    the .attribute is the default, trying to getattr to the link and the obj
    
    the + in front of an item will sum instead of joining

    grouped_objects = [(key, [(obj, lnk), (obj, lnk), ...]), ...]
    attributes  = [
        "#parent",
        ".PID",
        "#family",
        ".SizeName",
        ".Length:.2f",
        ".CuttingAngleA",
        ".CuttingAngleB",
        ".Cutout",
        "#count",
        ".Material",
        "+.ApproxWeight:.2f",
        ".Label"
    ]
    """

    def format_value(value, fmt=None):
        if isinstance(value, str):
            return value
    
        if fmt is None:
            return str(value)

        # if isinstance(value, App.Units.Quantity):
        #     value = value.Value

        return format(value, fmt)

    make_get_std_attr = lambda spec : lambda o, l : getattr(l, spec, getattr(o, spec, "N/A"))

    remove_quantity = lambda d : d.Value if isinstance(d, App.Units.Quantity) else d
    def round_if(val, dec=4):
        if isinstance(val, (float, App.Units.Quantity)):
            return round(val, dec)
        return val

    # build the list of functions that will work on each group of item
    header_functions = []
    for attr in attributes:

        # let's makes lambdas that will either join or sum the property 's content of the group element
        # the first one will make a list of all the element's property, the second will sum them
        make_group_func = lambda f : lambda l : list(set([round_if(remove_quantity(f(*i))) for i in l]))
        if attr.startswith('+'):
            attr = attr[1:]
            # the sum is encapsuled in a list to be of the same "dimension" of the other make_group_func
            make_group_func = lambda f : lambda l : [sum([round_if(remove_quantity(f(*i))) for i in l])]

        # get spec and fmt from attribute
        spec, *fmts = attr.split(':')
        fmt = fmts[0] if len(fmts) == 1 else None

        if spec.startswith('#'):
            f = funcs[spec[1:]]
        elif spec.startswith('.'):
            f = make_get_std_attr(spec[1:])
        else:
            raise ValueError(f'Unknow prefix, must be . or # : {spec}')


        make_format_func = lambda mgf, fmt : lambda l : ", ".join([format_value(i, fmt) for i in  mgf(l)])
        header_functions.append(make_format_func(make_group_func(f), fmt))


    data = []
    for key, objects in grouped_objects:
        row = [hf(objects) for hf in header_functions]
        data.append(row)

    return data