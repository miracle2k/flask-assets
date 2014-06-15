from __future__ import absolute_import

import sys
from nose import SkipTest
from flask import Flask
from flask.ext.assets import Environment, ManageAssets
from webassets.script import GenericArgparseImplementation
from tests.helpers import TempEnvironmentHelper

try:
    from flask.ext.script import Manager
except:
    raise SkipTest()


# The CLI likes to log to stderr, which isn't nice to the test output.
import logging
stdout_log = logging.getLogger(__name__)
stdout_log.addHandler(logging.StreamHandler(sys.stdout))


class TestScript(TempEnvironmentHelper):

    def test_call(self):
        # Setup the webassets.script with a mock main() function,
        # so we can check whether our call via Flask-Script actually
        # goes through.
        test_inst = self
        class DummyArgparseImplementation(GenericArgparseImplementation):
            def run_with_argv(self, argv):
                test_inst.last_script_call = argv
                return 0

        mgmt = Manager(self.app)
        mgmt.add_command('assets',
                ManageAssets(self.env, impl=DummyArgparseImplementation))

        try:
            # -h is a great test as that is something Flask-Script might
            # want to claim for itself.
            sys.argv = ['./manage.py', 'assets', '-h']
            mgmt.run()
        except SystemExit:
            # Always raised, regardless of success or failure of command
            pass
        assert self.last_script_call == ['-h']

    def test_call_auto_env(self):
        """Regression test: Passing the environment to the ManageAssets command
        is optional, it can be auto-detected."""
        mgmt = Manager(self.app)
        mgmt.add_command('assets', ManageAssets())

        try:
            # Used to raise an error due to the env not being properly set.
            sys.argv = ['./manage.py', 'assets', 'build']
            mgmt.run()
        except SystemExit:
            # Always raised, regardless of success or failure of command
            pass

    def test_parse_templates(self):
        """Test the --parse-templates option.
        """
        # Create a file in the app's templates directory
        self.app.template_folder = self.path('templates')
        self.create_files({
            'templates/template.html': """
            {% assets "in", output="output" %}
                {{ ASSET_URL }}
            {% endassets %}
            """,
            'in': "foo"
        })

        # Run the build command with --parse-templates, which should pick
        # up the bundle we defined in above template.
        mgmt = Manager(self.app)
        mgmt.add_command('assets', ManageAssets(log=stdout_log))
        mgmt.handle('test', ['assets', '--parse-templates', 'build'])

        assert self.exists('output')

