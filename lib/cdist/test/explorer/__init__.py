# -*- coding: utf-8 -*-
#
# 2010-2011 Steven Armstrong (steven-cdist at armstrong.cc)
#
# This file is part of cdist.
#
# cdist is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cdist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cdist. If not, see <http://www.gnu.org/licenses/>.
#
#

import os
import tempfile
import unittest
import shutil
import getpass

import cdist
from cdist import core
from cdist import test
from cdist.exec import local
from cdist.exec import remote
from cdist.core import explorer

import os.path as op
my_dir = op.abspath(op.dirname(__file__))
fixtures = op.join(my_dir, 'fixtures')
local_base_path = fixtures

class ExplorerClassTestCase(unittest.TestCase):

    def mkdtemp(self, **kwargs):
        return tempfile.mkdtemp(prefix='tmp.cdist.test.', **kwargs)

    def mkstemp(self, **kwargs):
        return tempfile.mkstemp(prefix='tmp.cdist.test.', **kwargs)

    def setUp(self):
        target_host = 'localhost'

        self.local_base_path = local_base_path
        self.out_path = self.mkdtemp()
        self.local = local.Local(target_host, self.local_base_path, self.out_path)
        self.local.create_directories()

        self.remote_base_path = self.mkdtemp()
        self.user = getpass.getuser()
        remote_exec = "ssh -o User=%s -q" % self.user
        remote_copy = "scp -o User=%s -q" % self.user
        self.remote = remote.Remote(target_host, self.remote_base_path, remote_exec, remote_copy)

        self.explorer = explorer.Explorer(target_host, self.local, self.remote)

    def tearDown(self):
        shutil.rmtree(self.out_path)
        shutil.rmtree(self.remote_base_path)

    def test_list_global_explorer_names(self):
        expected = ['global']
        self.assertEqual(self.explorer.list_global_explorer_names(), expected)

    def test_transfer_global_explorers(self):
        self.explorer.transfer_global_explorers()
        source = self.local.global_explorer_path
        destination = self.remote.global_explorer_path
        self.assertEqual(os.listdir(source), os.listdir(destination))

    def test_run_global_explorer(self):
        self.explorer.transfer_global_explorers()
        output = self.explorer.run_global_explorer('global')
        self.assertEqual(output, 'global\n')

    def test_list_type_explorer_names(self):
        cdist_type = core.Type(self.local.type_path, '__test_type')
        expected = cdist_type.explorers
        self.assertEqual(self.explorer.list_type_explorer_names(cdist_type), expected)

    def test_transfer_type_explorers(self):
        cdist_type = core.Type(self.local.type_path, '__test_type')
        self.explorer.transfer_type_explorers(cdist_type)
        source = os.path.join(self.local.type_path, cdist_type.explorer_path)
        destination = os.path.join(self.remote.type_path, cdist_type.explorer_path)
        self.assertEqual(os.listdir(source), os.listdir(destination))

    def test_transfer_object_parameters(self):
        cdist_type = core.Type(self.local.type_path, '__test_type')
        cdist_object = core.Object(cdist_type, self.local.object_path, 'whatever')
        cdist_object.parameters = {'first': 'first value', 'second': 'second value'}
        self.explorer.transfer_object_parameters(cdist_object)
        source = os.path.join(self.local.object_path, cdist_object.parameter_path)
        destination = os.path.join(self.remote.object_path, cdist_object.parameter_path)
        self.assertEqual(os.listdir(source), os.listdir(destination))

    def test_run_type_explorer(self):
        cdist_type = core.Type(self.local.type_path, '__test_type')
        cdist_object = core.Object(cdist_type, self.local.object_path, 'whatever')
        self.explorer.transfer_type_explorers(cdist_type)
        output = self.explorer.run_type_explorer('world', cdist_object)
        self.assertEqual(output, 'hello\n')
