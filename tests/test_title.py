# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import glob
import os
import re

import docutils.core
import testtools


class TestTitles(testtools.TestCase):
    def _get_title(self, section_tree):
        section = {
            'subtitles': [],
        }
        for node in section_tree:
            if node.tagname == 'title':
                section['name'] = node.rawsource
            elif node.tagname == 'section':
                subsection = self._get_title(node)
                section['subtitles'].append(subsection['name'])
        return section

    def _get_titles(self, spec):
        titles = {}
        for node in spec:
            if node.tagname == 'section':
                section = self._get_title(node)
                titles[section['name']] = section['subtitles']
        return titles

    def _check_titles(self, spec, titles):
        self.assertTrue(len(titles) >= 4,
                         "Titles count in '%s' doesn't match expected" % spec)
        problem = 'Problem description'
        self.assertIn(problem, titles)

        proposed = 'Proposed change'
        self.assertIn(proposed, titles)
        self.assertIn('Alternatives', titles[proposed], spec)

        impl = 'Implementation'
        self.assertIn(impl, titles)
        self.assertIn('Assignee(s)', titles[impl])
        self.assertIn('Work Items', titles[impl])

        deps = 'Dependencies'
        self.assertIn(deps, titles)

    def _check_lines_wrapping(self, tpl, raw):
        for i, line in enumerate(raw.split("\n")):
            if "http://" in line or "https://" in line:
                continue
            self.assertTrue(
                len(line) < 80,
                msg="%s:%d: Line limited to a maximum of 79 characters." %
                (tpl, i + 1))

    def _check_no_cr(self, tpl, raw):
        matches = re.findall('\r', raw)
        self.assertEqual(
            len(matches), 0,
            "Found %s literal carriage returns in file %s" %
            (len(matches), tpl))

    def _check_trailing_spaces(self, tpl, raw):
        for i, line in enumerate(raw.split("\n")):
            trailing_spaces = re.findall(" +$", line)
            msg = "Found trailing spaces on line %s of %s" % (i + 1, tpl)
            self.assertEqual(len(trailing_spaces), 0, msg)

    def test_template(self):
        # NOTE (e0ne): adding 'template.rst' to ignore dirs to exclude it from
        # os.listdir output
        ignored_dirs = {'template.rst', 'api',}

        files = ['specs/template.rst']

        # NOTE (e0ne): We don't check specs in 'api' directory because
        # they don't match template.rts. Uncomment code below it you want
        # to test them.
        # files.extend(glob.glob('specs/api/*/*'))

        releases = set(os.listdir('specs')) - ignored_dirs
        for release in releases:
            specs = glob.glob('specs/%s/*' % release)
            files.extend(specs)

        for filename in files:
            self.assertTrue(filename.endswith(".rst"),
                            "spec's file must use 'rst' extension.")
            if filename.split('/')[-1] != 'index.rst':
                with open(filename) as f:
                    data = f.read()

                spec = docutils.core.publish_doctree(data)
                titles = self._get_titles(spec)
                self._check_titles(filename, titles)
                #self._check_lines_wrapping(filename, data)
                self._check_no_cr(filename, data)
                self._check_trailing_spaces(filename, data)
