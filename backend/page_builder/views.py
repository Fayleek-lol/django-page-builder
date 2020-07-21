# -*- coding: utf-8 -*-

import os
import uuid
import json
import re

from django.utils import six
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.template import Template, Context
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test

from .settings import APP_MEDIA_DIR, PAGE_BUILDER_DIRNAME
from .fields import BuilderTemplate


def is_staff_check(user):
    return user.is_staff


def _make_path(alias, file_name):
    d = os.path.join(APP_MEDIA_DIR, alias[0:2], alias[2:4], alias)
    if not os.path.exists(d):
        os.makedirs(d)
    return os.path.join(APP_MEDIA_DIR, alias[0:2], alias[2:4], alias, file_name)


@login_required
@user_passes_test(is_staff_check)
def upload(request):
    data = {
        'code': 0,
        'response': 'upload error',
    }
    if request.method == 'POST':
        directory = request.POST['field_value']
        path = save_file(request.FILES['imageFileField'], directory)
        if path is not None:
            data['code'] = 1
            data['response'] = path

    return JsonResponse(data)


def save_file(f, d):
    extension = f.name.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4(), extension)
    path = _make_path(d, filename)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    url = settings.MEDIA_URL + PAGE_BUILDER_DIRNAME + '/' + d[0:2] + '/' + d[2:4] + '/' + d + '/' + filename
    return url


@login_required
@user_passes_test(is_staff_check)
def load(request):
    data = {}
    d = request.GET['field_value']
    path = _make_path(d, 'site.json')
    if os.path.isfile(path):
        with open(path) as data_file:
            data = json.load(data_file)
    return JsonResponse(data)


@login_required
@user_passes_test(is_staff_check)
def save(request):
    resp = {
        'responseCode': 0,
        'responseHTML': '<h5>Ouch!</h5> <p>Something went wrong and the site could not be saved :(</p>',
    }
    if request.method == 'POST':
        data = json.loads(request.body)
        d = data['field_value']
        path = _make_path(d, 'site.json')

        data = data.get('data', None)
        if data is None or data.get('delete'):
            data = {}

        with open(path, 'w') as outfile:
            json.dump(data, outfile)

        path = _make_path(d, 'templates.json')
        pages = data.get('pages', {})

        pages_keys = list(pages.keys())

        with open(path, 'w') as outfile:
            json.dump(pages_keys, outfile)

        # invalidate cache
        cache_keys = [BuilderTemplate.BUILDER_TEMPLATE_CACHE_KEY_PATTERN.format(d, name) for name in pages_keys]
        cache.delete_many(cache_keys)

        resp['responseCode'] = 1
        resp['responseHTML'] = '<h5>Hooray!</h5> <p>The site was saved successfully!</p>'

    return JsonResponse(resp)


@login_required
@user_passes_test(is_staff_check)
def preview(request):
    template_string = ''
    if request.method == 'POST':
        template_string = request.POST.get('page', '')
        template_string = template_string.replace("../bundles/", "/static/page_builder/elements/bundles/")

    t = Template(template_string)
    c = Context({})
    out = t.render(c)
    return HttpResponse(out)


@login_required
@user_passes_test(is_staff_check)
def export(request):
    result = "Page didn't save"
    if request.method == 'POST':
        d = request.POST['field_value']
        items = list(request.POST.items()) if six.PY3 else request.POST.iteritems()
        for key, value in items:
            if key.startswith('pages['):
                page_name = re.match(r'^pages\[(.*)\]', key).group(1)
                path = _make_path(d, page_name + '.html')
                page = value.replace("../bundles/", "/static/page_builder/elements/bundles/")
                page = re.sub('<div class="demo_page_builder">.*?</div>', '', page, flags=re.DOTALL)
                if six.PY2:
                    page = page.encode('utf-8')
                with open(path, 'w') as destination:
                    destination.write(page)
                    result = "Page saved"
    return HttpResponse(result)
