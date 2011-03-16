try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    raise ImportError(
        '''Flask extensions require pkg_resources.py, usually provided by
        setuptools. If setuptools is unavailable on your system
        (e.g. you're running on Google App Engine), you can obtain a copy
        from http://svn.python.org/projects/sandbox/trunk/setuptools/
        and place it somewhere on your Python path (e.g. alongside your
        main module).'''
        )
