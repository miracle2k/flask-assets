from nose.tools import assert_raises
from nose import SkipTest
from helpers import TempEnvironmentHelper


class TestFilters(TempEnvironmentHelper):

    def test_pyscss(self):
        """This filter used to make trouble because if required
        Environment.url and Environment.directory to be set.
        """
        try:
            import scss
        except ImportError:
            raise SkipTest()

        self.create_files({'foo': ''})
        bundle = self.mkbundle('foo', filters='pyscss', output='out')

        # By default we'd get an error, because the filter can't use
        # any good defaults.
        assert_raises(EnvironmentError, bundle.build)

        # If we set a director/url pair, it works.
        self.env.config['PYSCSS_STATIC_ROOT'] = 'a'
        self.env.config['PYSCSS_STATIC_URL'] = 'b'
        bundle.build()
