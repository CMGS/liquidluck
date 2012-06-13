#!/usr/bin/env python

import os
import datetime
from liquidluck.writers.base import get_post_slug, slug_to_destination
from liquidluck.writers.base import content_url, static_url
from liquidluck.writers.core import PostWriter, PageWriter
from liquidluck.writers.core import ArchiveWriter, ArchiveFeedWriter
from liquidluck.writers.core import FileWriter, StaticWriter
from liquidluck.options import settings, g

ROOT = os.path.abspath(os.path.dirname(__file__))


def test_get_post_slug():
    class Post:
        filename = 'demo'

        @property
        def category(self):
            return 'life'

        @property
        def date(self):
            return datetime.datetime(2012, 12, 12)

        @property
        def folder(self):
            return None

    post = Post()

    slug_format = '{{category}}/{{filename}}.html'
    assert get_post_slug(post, slug_format) == 'life/demo.html'

    slug_format = '{{date.year}}/{{filename}}.html'
    assert get_post_slug(post, slug_format) == '2012/demo.html'

    slug_format = '{{folder}}/{{filename}}.html'
    assert get_post_slug(post, slug_format) == 'demo.html'


def test_slug_to_destination():
    assert slug_to_destination('a/b.html') == 'a/b.html'
    assert slug_to_destination('a/b/') == 'a/b.html'
    assert slug_to_destination('a/b/', True) == 'a/b/index.html'
    assert slug_to_destination('a/b') == 'a/b.html'


def test_content_url():
    url = 'http://lepture.com'
    settings.site['url'] = url
    assert content_url('index.html') == (url + '/')

    settings.linktype = 'html'
    assert content_url(10) == '%s/10.html' % url
    assert content_url('a') == '%s/a.html' % url
    assert content_url('a.html') == '%s/a.html' % url
    assert content_url('a/') == '%s/a.html' % url
    assert content_url('a', 'b') == '%s/a/b.html' % url
    assert content_url('a/index.html') == '%s/a/' % url
    assert content_url('a/feed.xml') == '%s/a/feed.xml' % url
    assert content_url(10) == '%s/10.html' % url

    settings.linktype = 'clean'
    assert content_url('a') == '%s/a' % url
    assert content_url('a.html') == '%s/a' % url
    assert content_url('a/') == '%s/a' % url
    assert content_url('a', 'b') == '%s/a/b' % url
    assert content_url('a/index.html') == '%s/a/' % url
    assert content_url('a/feed.xml') == '%s/a/feed' % url
    assert content_url(10) == '%s/10' % url

    settings.linktype = 'slash'
    assert content_url('a') == '%s/a/' % url
    assert content_url('a.html') == '%s/a/' % url
    assert content_url('a/') == '%s/a/' % url
    assert content_url('a', 'b') == '%s/a/b/' % url
    assert content_url('a/index.html') == '%s/a/' % url
    assert content_url('a/feed.xml') == '%s/a/feed/' % url
    assert content_url(10) == '%s/10/' % url


def test_static_url():
    path = os.path.join(ROOT, 'source')
    func = static_url(path)
    func('settings.py')


class TestPostWriter(object):
    def test_start(self):
        #: if test_cli.py run first
        writer = PostWriter()
        writer.start()
        settings.permalink = '{{date.year}}/{{filename}}.html'
        writer.start()


class TestPageWriter(object):
    def test_start(self):
        writer = PageWriter()
        writer.start()
        f = os.path.join(g.output_directory, 'demo-page.html')
        assert os.path.exists(f)


class TestArchiveWriter(object):
    def test_start(self):
        writer = ArchiveWriter()
        writer.start()
        f = os.path.join(g.output_directory, 'index.html')
        assert os.path.exists(f)


class TestArchiveFeedWriter(object):
    def test_start(self):
        writer = ArchiveFeedWriter()
        writer.start()
        f = os.path.join(g.output_directory, 'feed.xml')
        assert os.path.exists(f)


class TestFileWriter(object):
    def test_start(self):
        writer = FileWriter()
        writer.start()
        f = os.path.join(g.output_directory, 'media/hold.txt')
        assert os.path.exists(f)


class TestStaticWriter(object):
    def test_start(self):
        writer = StaticWriter()
        writer.start()
        f = os.path.join(g.static_directory, 'style.css')
        assert os.path.exists(f)
