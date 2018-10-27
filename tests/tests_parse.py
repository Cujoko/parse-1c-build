# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import shutil
import tempfile
import unittest

from commons.compat import u
from parse_1c_build.cli import get_argparser
from parse_1c_build.parse import run as parse_run


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = get_argparser()

    def test_parse(self):
        temp_dir_fullname = u(tempfile.mkdtemp(), 'cp1251')
        args = self.parser.parse_args('parse tests/data/test.epf {0}'.format(temp_dir_fullname).split())
        parse_run(args)
        shutil.rmtree(temp_dir_fullname)
