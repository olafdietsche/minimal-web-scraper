#! /usr/bin/python
#
# -*- mode: python -*-
# Copyright (c) 2015 Olaf Dietsche
#

from lxml import etree
import http.cookiejar
import urllib.parse
import urllib.request

class AmbiguousPathError(Exception):
    pass

class PathNotFoundError(Exception):
    pass

class UserAgent:
    def __init__(self):
        cj = http.cookiejar.MozillaCookieJar()
        cp = urllib.request.HTTPCookieProcessor(cj)
        self.opener = urllib.request.build_opener(cp)
        self.parser = etree.HTMLParser()

    def get(self, url):
        response = self.opener.open(url)
        return response

    def post(self, url, data):
        response = self.opener.open(url, data)
        return response

    def parse(self, response):
        doc = etree.parse(response, self.parser)
        return doc

    def follow_link(self, response, doc, path):
        link = get_element(doc, path)
        url = urllib.parse.urljoin(response.url, link)
        return self.get(url)

class Form:
    def __init__(self, response, doc, path = '//form[1]'):
        form = get_element(doc, path)
        self._get_attributes(response.url, form)
        self.controls = dict()
        inputs = self._get_controls(form, './/input[@name and not(@disabled)]')
        self.controls.update(inputs)
        textareas = self._get_controls(form, './/textarea[@name and not(@disabled)]')
        self.controls.update(textareas)
        buttons = self._get_controls(form, './/button[@name and not(@disabled)]')
        self.controls.update(buttons)
        selects = self._get_selects(form)
        self.controls.update(selects)

    def submit(self, useragent, data = None):
        controls = self.controls
        controls.update(data)
        if self.method == 'get':
            query_string = urllib.parse.urlencode(controls)
            url = '{}?{}'.format(self.action, query_string)
            return useragent.get(url)

        if self.method == 'post':
            data = urllib.parse.urlencode(controls).encode('utf-8')
            request = urllib.request.Request(self.action)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=utf-8')
            return useragent.post(request, data)

    def _get_attributes(self, base_url, form):
        self.method = form.get('method') or 'get'
        self.method = self.method.lower()
        action = form.get('action')
        self.action = urllib.parse.urljoin(base_url, action)

    def _get_controls(self, form, path):
        controls = form.xpath(path)
        ret = dict()
        for elt in controls:
            name = elt.get('name')
            value = elt.get('value') or ''
            ret[name] = value

        return ret

    def _get_selects(self, form):
        selects = form.xpath('.//select[@name and not(@disabled)]')
        ret = dict()
        for elt in selects:
            name = elt.get('name')
            options = elt.xpath('.//option[@selected]')
            if (options is None or len(options) == 0):
                continue

            if (len(options) > 1):
                raise AmbiguousPathError('More than one option selected.', form, elt)

            value = options[0].get('value')
            ret[name] = value

        return ret

# Helper routines

def get_element(doc, path):
    elements = doc.xpath(path)
    if (elements is None or len(elements) == 0):
        return None

    if (len(elements) > 1):
        raise AmbiguousPathError("XPath matches more than one element.", doc, path)

    return elements[0]

def save_response(response, filename):
    with open(filename, 'wb') as f:
        buf = response.read(8192)
        while buf:
            f.write(buf)
            buf = response.read(8192)

def save_element(element, filename):
    with open(filename, 'wb') as f:
        html = etree.tostring(element)
        f.write(html)
