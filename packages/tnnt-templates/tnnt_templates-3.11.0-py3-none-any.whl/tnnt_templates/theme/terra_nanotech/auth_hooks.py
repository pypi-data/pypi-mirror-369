"""
Auth hooks for Terra Nanotech theme
"""

# Alliance Auth
from allianceauth import hooks
from allianceauth.theme.hooks import ThemeHook

# AA Templates: Terra Nanotech
from tnnt_templates.helper.static_files import get_theme_hook_static


class TerraNanotechThemeHook(ThemeHook):
    """
    Terra Nanotech Corp Auth Theme
    https://github.com/terra-nanotech/tn-nt-auth-templates/
    """

    def __init__(self):
        """
        Init
        """

        css_static_files = [
            get_theme_hook_static(
                static_file="tnnt_templates/theme/terra-nanotech/aav4/libs/bootstrap/v5.3.3/css/bootstrap.min.css"
            ),
            get_theme_hook_static(
                static_file="tnnt_templates/theme/terra-nanotech/aav4/css/terra-nanotech-defaults.min.css",
            ),
            get_theme_hook_static(
                static_file="tnnt_templates/theme/terra-nanotech/aav4/css/terra-nanotech-fonts.min.css",
            ),
            get_theme_hook_static(
                static_file="tnnt_templates/libs/fira-code/6.2.0/fira_code.min.css"
            ),
            get_theme_hook_static(
                static_file="tnnt_templates/libs/highlightjs/11.10.0/styles/github-dark.min.css"
            ),
            get_theme_hook_static(
                static_file="tnnt_templates/libs/highlightjs-copy/1.0.6/highlightjs-copy.min.css"
            ),
            get_theme_hook_static(
                static_file="tnnt_templates/theme/terra-nanotech/aav4/css/terra-nanotech.min.css",
            ),
            get_theme_hook_static(
                static_file="tnnt_templates/theme/terra-nanotech/aav4/css/community-app-fixes.min.css",
            ),
        ]

        js_static_files = [
            get_theme_hook_static(
                static_file="tnnt_templates/theme/terra-nanotech/aav4/libs/popper/v2.11.8/popper.min.js"
            ),
            get_theme_hook_static(
                static_file="tnnt_templates/theme/terra-nanotech/aav4/libs/bootstrap/v5.3.3/javascript/bootstrap.min.js"
            ),
            get_theme_hook_static(
                static_file="tnnt_templates/libs/highlightjs-copy/1.0.6/highlightjs-copy.min.js"
            ),
            get_theme_hook_static(
                static_file="tnnt_templates/javascript/terra-nanotech.min.js",
                script_type="module",
            ),
        ]

        ThemeHook.__init__(
            self=self,
            name="Terra Nanotech",
            description="Terra Nanotech Corp Auth Theme",
            html_tags={"data-theme": "terra-nanotech"},
            css=css_static_files,
            js=js_static_files,
            header_padding="3.5em",
        )


@hooks.register("theme_hook")
def register_terra_nanotech_hook():
    """
    Registers the Terra Nanotech theme hook

    :return:
    :rtype:
    """

    return TerraNanotechThemeHook()
