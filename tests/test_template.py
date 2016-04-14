import unittest

from template import render
from utils import get_random_string

__author__ = 'pahaz'


class TemplateTestCase(unittest.TestCase):
    def test_render_variable(self):
        name = get_random_string()
        template = 'My name {{ name }}'
        result = render(template, {'name': name})
        self.assertEqual(result, 'My name ' + name)

    def test_render_for_block(self):
        template = 'Users: {% for name in names %}{{name}}, {% endfor %}'
        result = render(template, {'names': ['pahaz', 'admin', 'user']})
        self.assertEqual(result, 'Users: pahaz, admin, user')

    def test_render_empty_for_block(self):
        template = 'Users: {% for name in names %}{{name}}, {% endfor %}'
        result = render(template, {'names': []})
        self.assertEqual(result, 'Users: ')

    def test_render_if_block_with_condition_true(self):
        secret = get_random_string()
        template = 'My secret {% if is_admin %}' + secret+ '{% endfor %}'
        result = render(template, {'is_admin': True})
        self.assertEqual(result, 'My secret ' + secret)

    def test_render_if_block_with_condition_false(self):
        secret = get_random_string()
        template = 'My secret {% if is_admin %}' + secret + '{% endfor %}'
        result = render(template, {'is_admin': False})
        self.assertEqual(result, 'My secret ')

    def test_render_if_else_block_with_condition_true(self):
        pass

    def test_render_if_else_block_with_condition_false(self):
        pass
