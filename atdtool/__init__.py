#!/usr/bin/python

import re
import urllib
import base64
from xml.etree import ElementTree
try:
    import httplib
except ImportError:
    import http.client as httplib


PROGRAM_NAME = "atdtool"
PROGRAM_VERSION = "1.3.2"


def checkDocument(cfg, fd):
    '''Invoke checkDocument service and return a list of errors.'''

    server = re.sub(r'^https?://', '', cfg.server)

    if cfg.atdlang != '':
        server = cfg.atdlang + '.' + server

    if cfg.server.startswith('https'):
        service = httplib.HTTPSConnection(server, cfg.port)
    else:
        service = httplib.HTTPConnection(server, cfg.port)

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if cfg.username:
        headers["Authorization"] = "Basic %s" % \
            (base64.b64encode("%s:%s" % (cfg.username, cfg.password)))

    params = {'key': cfg.key, 'data': fd.read()}
    if cfg.lang != '':
        params['lang'] = cfg.lang

    service.request(method='POST',
                    url='/checkDocument',
                    body=urllib.urlencode(params),
                    headers=headers)
    response = service.getresponse()
    if response.status != httplib.OK:
        service.close()
        raise Exception('Unexpected response code from AtD server %s: %d' %
                        (cfg.server, response.status))

    print(response.read())
    et = ElementTree.fromstring(response.read())
    service.close()

    errs = et.findall('message')
    if len(errs) > 0:
        raise Exception('Server returned an error: %s' % errs[0].text)
    return [Error(e) for e in et.findall('error')]


class Error(object):

    '''Error objects.

    >>> xmlstr = '<error>\
            <string>sysexit</string>\
            <description>Spelling</description>\
            <precontext></precontext>\
            <suggestions>\
            <option>sexist</option>\
            <option>systemic</option>\
            <option>syenite</option>\
            <option>seit</option>\
            </suggestions>\
            <type>spelling</type>\
            </error>'
    >>> et = ElementTree.fromstring(xmlstr)
    >>> e = Error(et)
    >>> import sys
    >>> showerrs('', sys.stdout, [e])
    :1:0: (?) Spelling ""
      suggestions: sexist, systemic, syenite, seit
    '''

    def __init__(self, e):
        self.string = e.find('string').text
        self.description = e.find('description').text
        self.precontext = e.find('precontext').text
        self.type = e.find('type').text
        self.url = ''
        if not e.find('url') is None:
            self.url = e.find('url').text
        self.suggestions = []
        if not e.find('suggestions') is None:
            self.suggestions = [
                o.text for o in e.find('suggestions').findall('option')
            ]


class FileWords:

    '''Parser class, keeps line and column position.'''

    def __init__(self, fd):
        fd.seek(0)
        self.re = re.compile('([^a-z0-9A-Z_-])')
        self.skipre = re.compile('[^a-z0-9A-Z_-]+')
        self.text = self.re.split(fd.read())
        self.len = len(self.text)
        self.reset()

    def reset(self):
        '''Goes to start of file.'''
        self.i = 0
        self.line = 1
        self.col = 0
        self.eof = False

    def next(self):
        '''Goes to next token.'''
        if self.eof:
            return
        self.col = self.col + len(self.text[self.i])
        self.i = self.i + 1
        if self.i >= self.len:
            self.eof = True
            return
        if self.text[self.i] == '\n':
            self.line = self.line + 1
            self.col = 0

    def skipnw(self):
        '''Skips non-word tokens.'''
        while self.skipre.match(self.text[self.i]) or self.text[self.i] == '':
            self.next()

    def checkpos(self, words0):
        '''Checks if words0 is in current position.'''
        words = tuple(self.re.split(words0))
        text = self.text
        t = []
        j = 0
        w = ''
        while len(t) < len(words):
            if self.i + j == self.len:
                self.eof = True
                return False, ''
            t.append(text[self.i + j])
            w = w + text[self.i + j]
            if self.i + j + 1 < self.len and text[self.i + j + 1] == '.':
                t.append(t.pop() + text[self.i + j + 2])
                w = w + '.' + text[self.i + j + 2]
            j = j + 1
        return tuple(t) == words, w

    def goto(self, prec, words):
        '''Goes to words preceded by prec;
        returns False and stays at eof if not found.'''
        found = False
        w = ''
        if prec:
            target = prec
        else:
            target = words
        while not self.eof and not found:
            found, w = self.checkpos(target)
            if not found:
                self.next()
            elif prec:
                self.next()
                self.skipnw()
                found, w = self.checkpos(words)
        if found:
            self.words = w
            return True
        return False

    def find(self, prec, words):
        '''Tries to find words preceded by prec from current position,
        then from start of file.'''
        found = self.goto(prec, words)
        if not found:
            self.reset()
            found = self.goto(prec, words)
        return found


def showerrs(filename, fd, errs):
    '''Shows the errors found, in the context of the file.'''
    t = FileWords(fd)
    for e in errs:
        exactstr = ''
        if not t.find(e.precontext, e.string):
            exactstr = ' (?)'
        print('%s:%d:%d:%s %s "%s"' %
              (filename,
                  t.line,
                  t.col,
                  exactstr,
                  e.description,
                  t.words if hasattr(t, 'words') else ''))
        if len(e.suggestions) > 0:
            print('  suggestions: %s' % ', '.join(e.suggestions))
