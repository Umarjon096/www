# -*- coding: utf-8 -*-

from urllib.parse import urlencode
from collections import OrderedDict
from django import template

register = template.Library()

@register.simple_tag
def url_replace(request, field, value, direction=''):
    dict_ = request.GET.copy()

    if field == 'order_by' and field in dict_.keys():
      if dict_[field].startswith('-') and dict_[field].lstrip('-') == value:
        dict_[field] = value
      elif dict_[field].lstrip('-') == value:
        dict_[field] = "-" + value
      else:
        dict_[field] = direction + value
    else:
      dict_[field] = direction + value
    t = OrderedDict(sorted(dict_.items()))
    return urlencode(OrderedDict(sorted(dict_.items())))

@register.simple_tag
def url_replace2(request):
    maintain_order = []
    dict_ = request.GET.copy()
    if 'order_by' in dict_.keys():
        maintain_order.append(('order_by',dict_['order_by'],))
    return urlencode(maintain_order)