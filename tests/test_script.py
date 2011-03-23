import sys
from nose import SkipTest
from flask import Flask
from flaskext.assets import Environment, ManageAssets

try:
    from flaskext.script import Manager
except:
    raise SkipTest()


class TestScript:

    def setup(self):
        self.app = Flask(__name__)
        self.env = Environment(self.app)
        self.mgmt = Manager(self.app)
        self.mgmt.add_command('assets', ManageAssets(self.env))

        # Setup the webassets.script with a mock main() function,
        # so we can check whether our call via Flask-Script actually
        # goes through.
        def dummy_main(argv, *a, **kw):
            self.last_script_call = argv
            return 0
        from webassets import script
        script.main = dummy_main

    def test_call(self):
        try:
            # -h is a great test as that is something Flask-Script might
            # want to claim for itself.
            sys.argv = ['./manage.py', 'assets', '-h']
            self.mgmt.run()
        except SystemExit:
            # Always raised, regardless of success or failure of command
            pass
        assert self.last_script_call == ['-h']