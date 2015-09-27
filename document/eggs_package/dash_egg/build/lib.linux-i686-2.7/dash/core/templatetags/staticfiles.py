from django import template
from django.template import Context, Template
import pdb
from django.conf import settings
register = template.Library()

class Static(template.Node):
    def __init__(self, nav_path, nav_displaytext):
        self.path = nav_path.strip('"')
        self.text = nav_displaytext.strip('"')

    @register.tag(name='static')
    def static(parser, token):
        try:
            tag_name, nav_path = token.split_contents()
        except ValueError:
            raise template.TemplateSyntaxError, \
                    "%r tag requires exactly two arguments: path and text" % \
                    token.split_contents[0]

        return Static(nav_path,tag_name)

    def render(self, context):
        t = Template(settings.STATIC_URL+self.path.replace("'",""))
        return t.render(context)
