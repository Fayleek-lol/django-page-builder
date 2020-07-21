# -*- coding: utf-8 -*-

import os
import uuid
import json

from django import forms

from django.core import exceptions
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .widgets import PageBuilderWidget
from .settings import APP_MEDIA_DIR, ELEMENTS, CACHE_DURATION


class empty:
    """
    This class is used to represent no data being provided for a given input
    or output value.

    It is required because `None` may be a valid input or output value.
    """
    pass


class BuilderTemplate(object):

    BUILDER_TEMPLATE_CACHE_KEY_PATTERN = 'bldr_tmpl:{0}:{1}'

    def __init__(self, dirname=None):
        if dirname is None:
            dirname = uuid.uuid4().hex

        self.dirname = dirname
        self.path = os.path.join(APP_MEDIA_DIR, dirname[0:2], dirname[2:4], dirname)

        # *** test ***
        # print ("===============================================")
        # print ("===============================================")
        # print (self.read_template(name="page2"))
        # print ("===============================================")
        # print ("===============================================")

    def __len__(self):
        return self.dirname.__len__()

    def __str__(self):
        return self.dirname

    def read_template(self, name=None):
        key = BuilderTemplate.BUILDER_TEMPLATE_CACHE_KEY_PATTERN.format(self.dirname, name)
        value = cache.get(key, empty)
        if value == empty:
            value = self.force_read_template(name)
            cache.set(key, value, CACHE_DURATION)
        return value

    def force_read_template(self, name=None):
        templates = self.get_templates()
        if len(templates):
            if name is None:
                name = templates[0]
            elif name not in templates:
                return None
            path = os.path.join(self.path, name + '.html')
            with open(path) as data_file:
                data = data_file.read()
                return data
        return None

    def get_templates(self):
        path = os.path.join(self.path, 'templates.json')
        if os.path.isfile(path):
            with open(path) as data_file:
                return json.load(data_file)
        return []


class BuilderTemplateFormField(forms.CharField):
    widget = PageBuilderWidget

    default_error_messages = {
        'invalid': _('Enter a valid UUID.'),
    }

    def __init__(self, *args, **kwargs):

        self.elements = kwargs.pop("elements", ELEMENTS)
        if self.elements is None:
            self.elements = ELEMENTS

        super(BuilderTemplateFormField, self).__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super(BuilderTemplateFormField, self).widget_attrs(widget)
        attrs['elements'] = json.dumps(self.elements)
        return attrs

    def prepare_value(self, value):
        if value is None:
            return BuilderTemplate()
        return value

    def to_python(self, value):
        value = super(BuilderTemplateFormField, self).to_python(value)
        if value in self.empty_values:
            return None
        if not isinstance(value, BuilderTemplate):
            try:
                value = uuid.UUID(value)
            except ValueError:
                raise exceptions.ValidationError(self.error_messages['invalid'], code='invalid')
            else:
                value = BuilderTemplate(dirname=value.hex)
        return value


class BuilderTemplateField(models.Field):

    default_error_messages = {
        'invalid': _("'%(value)s' is not a valid UUID."),
    }

    def __init__(self, *args, **kwargs):
        self.elements = kwargs.pop("elements", None)

        # kwargs['max_length'] = 32

        super(BuilderTemplateField, self).__init__(*args, **kwargs)

    # def deconstruct(self):
    #     name, path, args, kwargs = super(BuilderTemplateField, self).deconstruct()
    #     del kwargs['max_length']
    #     return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'form_class': BuilderTemplateFormField,
            'elements': self.elements
        }
        defaults.update(kwargs)
        return super(BuilderTemplateField, self).formfield(**defaults)

    def get_internal_type(self):
        return "CharField"

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        if not isinstance(value, BuilderTemplate):
            try:
                value = uuid.UUID(value)
            except AttributeError:
                raise TypeError(self.error_messages['invalid'] % {'value': value})
            else:
                value = BuilderTemplate(dirname=value.hex)
        return value.dirname

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        if value and not isinstance(value, BuilderTemplate):
            try:
                value = uuid.UUID(value)
            except ValueError:
                value = None
            else:
                value = BuilderTemplate(dirname=value.hex)
        return value

    def to_python(self, value):
        if value is None:
            return value
        if value and not isinstance(value, BuilderTemplate):
            try:
                value = uuid.UUID(value)
            except ValueError:
                raise exceptions.ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': value},
                )
            else:
                return BuilderTemplate(dirname=value.hex)
        return value
