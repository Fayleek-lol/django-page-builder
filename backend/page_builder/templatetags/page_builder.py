# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from functools import reduce

from django.template import Library, Template, Context
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils import six

from classytags.core import Tag, Options
from classytags.arguments import Argument

register = Library()


class RenderTemplate(Tag):
    name = 'render_template'
    options = Options(
        Argument('template'),
        Argument('name', required=False),
    )
    def render_tag(self, context, template, name=None):
        template_string = template.read_template(name)
        t = Template(template_string)
        c = Context(context)
        return t.render(c)

register.tag(RenderTemplate)


class UpdateContext(Tag):
    name = 'updatecontext'
    options = Options(
        blocks=[('endupdatecontext', 'nodelist')],
    )

    def render_tag(self, context, nodelist):
        block_data = json.loads(
            reduce(
                lambda x, y: x + force_text(y),
                map(
                    lambda x: getattr(x, 's', None) and x.s or x.render(context),
                    nodelist
                )
            )
        )
        context.update(block_data)
        return ""


register.tag(UpdateContext)


@register.simple_tag(name='chr')
def char(value):
    try:
        ret = unicode(chr(value))
    except NameError:
        ret = chr(value)
    return mark_safe(ret)
