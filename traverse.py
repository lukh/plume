from collections import defaultdict
import FreeCAD as App
import FreeCADGui as Gui

from itertools import groupby
from collections import defaultdict

from .utils import *

def get_parents(obj):
    return reversed([p[0] for p in obj.Parents])

def get_parents_groups(obj):
    def scan(obj):
        pg = obj.getParentGroup()
        if pg is not None:
            yield from scan(pg)
            yield pg

    l = list(scan(obj))
    return l

def get_parents_path(obj):
    p = get_parents(obj)
    pg = get_parents_groups(obj)

    return "/".join([x.Label for x in p]) + ":" + "/".join([y.Label for y in pg])

def traverse(obj, include_subpartcontainers=True, deepness=None,
        include_if_any=[],
        exclude_if_any=[]
    ):
    """
    A Generic function to traverse and yield objects in a Part Container, or an Assembly
    :include_subpartcontainers : include sub containers in the list 
    :deepness : traverse recursivity, None for no infinity, or an integer (0 for first level, 1 for the two first levels, etc)
    :include_if_any: include the object if any of the conditions are True
    :exclude_if_any: exclude the object if any of the conditions are True

    Yield (element, source_object)
    """
    # filter all FF objects : Profiles, Trimmed, and Extruded. + Links (and VariantLinks ??)
    # TODO : can we have other kind of object ?? Such as Body/PartFeature (Mirror... ) ???
    #        If they have a PID it's ok ?

    # is_profile(o) or is_trimmedbody(o) or is_extrudedcutout(o)

    elements = [o for o in obj.Group 
        if (
            is_variant(o) or 
            #o.TypeId == "App::Link" or 
            any([f(o) for f in include_if_any]))
        and not any([f(o) for f in exclude_if_any])
    ]

    ignored_set = set()

    # TODO try to find a better solution to catch children
    for e in elements:
        # a Variant Link will "claim children", so if it is a VariantLink, let's check 

        if not is_variant(e): # NOT A VariantLink
            # Group contains all elements.
            # ignore "childrens" (from claimChildren) will avoid to get noise, ie, for instance, 
            # profiles used as a base for other profiles in frameforge, or feature in Body.
            ignored_set.update(e.ViewObject.claimChildren())

        else: # a Variant Link
            ignored_set.add(e)
            if not e.Enable : # Disabled Variant Link :
                print("Ignoring", e.Label, e.Source.Label)
                # add the direct children to ignored set, else keep it as element
                ignored_set.update(e.ViewObject.claimChildren())


    elements_set = set(elements) - ignored_set
    elements = list(elements_set)

    for e in elements:
        if e.TypeId == "App::Link": # either a FFLink, or an Assembly Link ?
            # for a sub part, ie a PartContainer or a Assembly Object

            # TODO : recursly find src ???? (link of link)
            e_src = get_link(e)

            if is_part(e_src) or e_src.TypeId == 'Assembly::AssemblyObject':
                if include_subpartcontainers:
                    yield (e, e_src)

                # recursive call
                if (deepness is None) or (deepness > 0):
                        nd = deepness-1 if deepness is not None else None
                             
                        yield from traverse(
                            e, 
                            include_subpartcontainers=include_subpartcontainers, 
                            deepness=nd,
                            include_if_any=include_if_any,
                            exclude_if_any=exclude_if_any
                        )
            
            # this is a simple link (FF or Assembly)
            else:
                yield (e, e_src)

        else:
            yield (e, e)
    



# selection = Gui.Selection.getSelection()
# obj = selection[0]

# ####################################################################################################
# ## RAW LIST ###
# include_if_any=[is_profile, is_trimmedbody, is_extrudedcutout, is_part_or_part_design]
# print()
# print()
# print()
# print("TOP LEVEL ONLY")
# elements = list(traverse(obj, deepness=0, include_if_any=include_if_any))
# for x in [(get_parents_path(e), e.Label, e.Name, l.Name) for e, l in elements]:
#     print(x)


# print()
# print("TOP LEVEL Without SubContainer")
# elements = list(traverse(obj, deepness=0, include_subpartcontainers=False, include_if_any=include_if_any))
# for x in [(get_parents_path(e), e.Label, e.Name, l.Name) for e, l in elements]:
#     print(x)

# print()
# print("FULL LEVEL With SubContainer")
# elements = list(traverse(obj, deepness=None, include_if_any=include_if_any))
# for x in [(get_parents_path(e), e.Label, e.Name, l.Name) for e, l in elements]:
#     print(x)

# print()
# print("FULL LEVEL Without SubContainer")
# elements = list(traverse(obj, deepness=None, include_subpartcontainers=False, include_if_any=include_if_any))
# for x in [(get_parents_path(e), e.Label, e.Name, l.Name) for e, l in elements]:
#     print(x)
# ####################################################################################################






def group_elements_by(elements, groupby_obj = [], groupby_src = []):
    """
    Group elements by the groupby list

    :groupby: (["Property", lambda, ...], ["Property", lambda, ...])
    """

    def round_if(val, dec=4):
        if isinstance(val, (float, App.Units.Quantity)):
            return round(val, dec)
        return val


    group_by_func = lambda el : tuple(
        [round_if(getattr(el[0], gbo, None) if isinstance(gbo, str) else gbo(el[0])) for gbo in groupby_obj] +
        [round_if(getattr(el[1], gbc, None) if isinstance(gbc, str) else gbc(el[1])) for gbc in groupby_src]
    )

    sorted_elements = sorted(elements, key = group_by_func)

    return [
        (key, list(group))
        for key, group in groupby(sorted_elements, group_by_func)
    ]



# def make_list(elements, 
#         columns=[
#             ("obj", lambda o : get_parents_path(o)), 
#             ("obj", "Name"),
#             ("obj", "PID"),
#             ("lnk", "PlumeIPN"),
#         ],
#         groupby=[
#             ('obj', lambda o : get_parents_path(o)), 
#             ('lnk', "PlumeIPN"),
#         ]
#     )


# include_if_any=[is_profile, is_trimmedbody, is_extrudedcutout, is_part_or_part_design]
# print("Top Level")
# elements = list(traverse(obj, deepness=0, include_if_any=include_if_any))
# for x in [(get_parents_path(e), e.Label, e.Name, l.Name) for e, l in elements]:
#     print(x)

# print("GROUP")
# group_elements_by(elements, groupby_src=["Name"])

# # exclude the object if any of the conditions are True
# include_if_any=[is_profile, is_trimmedbody, is_extrudedcutout]
# exclude_if_any=[lambda x : not (is_profile(x) or is_trimmedbody(x) or is_extrudedcutout(x))]

# print("list prof types")
# elements = list(traverse(obj, deepness=0, include_if_any=include_if_any, exclude_if_any=exclude_if_any))
# for x in [(get_parents_path(e), e.Label, e.Name, l.Name) for e, l in elements]:
#     print(x)

# print("GROUP")
# grouped_elements = group_elements_by(elements, groupby_src=["Family", "SizeName"])