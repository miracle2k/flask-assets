import sys, os

# In order to test the Flask-Script command, Flask-Script needs to be
# installed. If this is the case, we won't be able to import from our
# local src/flaskext directory that nose puts on sys.path, due to the
# way Flask extensions employ pkg_resources to have multiple directories
# contribute to the same module. We fix it by manually adding the
# directory to an already existing virtual flaskext module.
try:
    sys.modules['flaskext'].__path__.append(
        os.path.join(os.path.dirname(__file__), '../src/flaskext'))
except KeyError:
    pass