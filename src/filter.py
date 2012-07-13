"""Flask specific filters.

For those to be registered automatically, make sure the main flask-assets
namespace imports this file.
"""


from flask.templating import render_template_string
from webassets.filter import Filter, register_filter


class Jinja2TemplateFilter(Filter):
    """Will compile all source files as Jinja2 temlates using the standard
    Flask contexts.
    """
    name = 'jinja2template'

    def __init__(self, context=None):
        super(Jinja2TemplateFilter, self).__init__()
        self.context = context or {}

    def input(self, _in, out, source_path, output_path, **kw):
        out.write(render_template_string(_in.read(), **self.context))


register_filter(Jinja2TemplateFilter)
