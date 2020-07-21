# -*- coding: utf-8 -*-

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils import six


class PageBuilderWidget(forms.Widget):

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js',)
        css = {
            'all': ('page_builder/css/font-awesome.css',)
        }

    def render(self, name, value, attrs=None):
        a_kwargs = {'extra_attrs': {'name': name}} if six.PY3 else {'name': name}
        final_attrs = self.build_attrs(attrs, **a_kwargs)

        if six.PY3 and self.attrs.get('elements', None) is not None:
            final_attrs['elements'] = self.attrs['elements']

        if final_attrs.get('elements', None) is None:
            final_attrs['elements'] = '[]'

        return mark_safe(
            render_to_string('page_builder/index.html', {
                'value': value,
                'final_attrs': final_attrs
            })
        )
