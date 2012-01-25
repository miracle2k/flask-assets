from __future__ import with_statement

import sys
from nose import SkipTest
from flask import Flask
from flask.ext.assets import Environment, ManageAssets

try:
    from flaskext.script import Manager
except:
    raise SkipTest()


class TestScript:

    def setup(self):
        self.app = Flask(__name__)
        self.env = Environment(self.app)

    def test_call(self):
        # Setup the webassets.script with a mock main() function,
        # so we can check whether our call via Flask-Script actually
        # goes through.
        def dummy_main(argv, *a, **kw):
            self.last_script_call = argv
            return 0
        from webassets import script
        old_main = script.main
        script.main = dummy_main

        try:
            mgmt = Manager(self.app)
            mgmt.add_command('assets', ManageAssets(self.env))

            try:
                # -h is a great test as that is something Flask-Script might
                # want to claim for itself.
                sys.argv = ['./manage.py', 'assets', '-h']
                mgmt.run()
            except SystemExit:
                # Always raised, regardless of success or failure of command
                pass
            assert self.last_script_call == ['-h']
        finally:
            script.main = old_main

    def test_call_auto_env(self):
        """Regression test: Passing the environment to the ManageAssets command
        is optional, it can be auto-detected."""
        mgmt = Manager(self.app)
        mgmt.add_command('assets', ManageAssets())

        try:
            # Used to raise an error due to the env not being properly set.
            sys.argv = ['./manage.py', 'assets', 'rebuild']
            mgmt.run()
        except SystemExit:
            # Always raised, regardless of success or failure of command
            pass
        
