# -*- coding: utf-8 -*-
'''
Blog content file parser.

Syntax::

    # Title

    - date: 2011-09-01
    - folder: life
    - tags: tag1, tag2

    -----------------

    Your content here. And it support code highlight.

    ```python

    def hello():
        return 'Hello World'

    ```


:copyright: (c) 2012 by Hsiaoming Yang (aka lepture)
:license: BSD
'''


import re
import logging
import misaka as m

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from liquidluck.readers.base import BaseReader, Post
from liquidluck.utils import to_unicode


class MarkdownReader(BaseReader):
    SUPPORT_TYPE = ['md', 'mkd', 'markdown']

    def render(self):
        f = open(self.filepath)
        logging.info('read ' + self.filepath)

        header = ''
        body = None
        for line in f:
            if line.startswith('---'):
                body = ''
            elif body is not None:
                body += line
            else:
                header += line

        f.close()

        meta = self._parse_meta(header)
        content = markdown(body)
        return Post(self.filepath, content, meta=meta)

    def _parse_meta(self, header):
        header = markdown(header)
        title = re.findall(r'<h1>(.*)</h1>', header)[0]

        meta = {'title': title}
        items = re.findall(r'<li>(.*?)</li>', header, re.S)
        for item in items:
            index = item.find(':')
            key = item[:index].rstrip()
            value = item[index + 1:].lstrip()
            meta[key] = value

        return meta


class JuneRender(m.HtmlRenderer, m.SmartyPants):
    def paragraph(self, text):
        cjk = re.compile(
            ur'([\u4e00-\u9fff]+?)'
            r'(\n|\r\n|\r)'
            ur'([\u4e00-\u9fff]+?)'
        )
        text = cjk.sub(r'\1\3', text)
        return '<p>%s</p>\n' % text

    def block_code(self, text, lang):
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            return '\n<pre><code>%s</code></pre>\n' % escape(text.strip())

        formatter = HtmlFormatter()
        return highlight(text, lexer, formatter)

    def autolink(self, link, is_email):
        title = link.replace('http://', '').replace('https://', '')

        #: youtube.com
        pattern = r'http://www.youtube.com/watch\?v=([a-zA-Z0-9\-\_]+)'
        match = re.match(pattern, link)
        if not match:
            pattern = r'http://youtu.be/([a-zA-Z0-9\-\_]+)'
            match = re.match(pattern, link)
        if match:
            value = ('<iframe width="560" height="315" src='
                     '"http://www.youtube.com/embed/%(id)s" '
                     'frameborder="0" allowfullscreen></iframe>'
                     '<div><a rel="nofollow" href="%(link)s">'
                     '%(title)s</a></div>'
                    ) % {'id': match.group(1), 'link': link, 'title': title}
            return value

        #: gist support
        pattern = r'(https?://gist.github.com/[\d]+)'
        match = re.match(pattern, link)
        if match:
            value = ('<script src="%(link)s.js"></script>'
                     '<div><a rel="nofollow" href="%(link)s">'
                     '%(title)s</a></div>'
                    ) % {'link': match.group(1), 'title': title}
            return value

        #: vimeo.com
        pattern = r'http://vimeo.com/([\d]+)'
        match = re.match(pattern, link)
        if match:
            value = ('<iframe width="500" height="281" frameborder="0" '
                     'src="http://player.vimeo.com/video/%(id)s" '
                     'allowFullScreen></iframe>'
                     '<div><a rel="nofollow" href="%(link)s">'
                     '%(title)s</a></div>'
                    ) % {'id': match.group(1), 'link': link, 'title': title}
            return value
        if is_email:
            return '<a href="mailto:%(link)s">%(link)s</a>' % {'link': link}

        return '<a href="%s">%s</a>' % (link, title)


def markdown(text):
    text = to_unicode(text)
    render = JuneRender(flags=m.HTML_USE_XHTML)
    md = m.Markdown(
        render,
        extensions=m.EXT_FENCED_CODE | m.EXT_AUTOLINK,
    )
    return md.render(text)


_XHTML_ESCAPE_RE = re.compile('[&<>"]')
_XHTML_ESCAPE_DICT = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}


def escape(value):
    """Escapes a string so it is valid within XML or XHTML."""
    if not isinstance(value, (basestring, type(None))):
        value = value.decode('utf-8')
    return _XHTML_ESCAPE_RE.sub(
        lambda match: _XHTML_ESCAPE_DICT[match.group(0)], value)