from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()


@register.filter
def return_item(l, i):
    try:
        return l[i]
    except:
        return None
    
    
@register.simple_tag
def multiple_add(merged_list,*args):
    merged_list = str(merged_list)
    for element in args:
        merged_list = merged_list + element
    return merged_list
    

    
    
    
#@register.filter(name='list_iter')
#def list_iter(lists):
#    list_a, list_b, list_c = lists
#
#    for x, y, z in zip(list_a, list_b, list_c):
#        yield (x, y, z)
