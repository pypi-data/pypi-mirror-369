# Django
from django.template import Context, Template
from django.test import TestCase, modify_settings

# AA Templates: Terra Nanotech
from tnnt_templates import __version__


class TestTnntTemplateVariables(TestCase):
    """
    Test TN-NT Template tags
    """

    def setUp(self):
        self.context = Context(
            {"content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."}
        )

    def test_should_return_content_when_string_starts_with_substring(self):
        template_to_render = Template(
            "{% load tnnt_template_tags %}"
            '{% if content|startswith:"Lorem" %}{{ content }}{% endif %}'
        )
        rendered_template = template_to_render.render(self.context)
        self.assertInHTML(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            rendered_template,
        )

    def test_should_not_return_content_when_string_does_not_start_with_substring(self):
        template_to_render = Template(
            "{% load tnnt_template_tags %}"
            '{% if content|startswith:"ipsum" %}{{ content }}{% endif %}'
        )
        rendered_template = template_to_render.render(self.context)
        self.assertNotIn(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            rendered_template,
        )

    @modify_settings(INSTALLED_APPS={"append": "aagdpr"})
    def test_should_return_true_when_app_is_installed(self):
        template_to_render = Template(
            "{% load tnnt_template_tags %}"
            '{% is_app_installed "aagdpr" as is_myapp_installed %}'
            "{% if is_myapp_installed %}True{% else %}False{% endif %}"
        )
        rendered_template = template_to_render.render(Context({"version": __version__}))
        self.assertEqual(rendered_template, "True")

    @modify_settings(INSTALLED_APPS={"remove": "aagdpr"})
    def test_should_return_false_when_app_is_not_installed(self):
        template_to_render = Template(
            "{% load tnnt_template_tags %}"
            '{% is_app_installed "aagdpr" as is_myapp_installed %}'
            "{% if is_myapp_installed %}True{% else %}False{% endif %}"
        )
        rendered_template = template_to_render.render(Context({"version": __version__}))
        self.assertEqual(rendered_template, "False")
