"""
TNNT Auth Templates auth hooks module
"""

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import UrlHook

# AA Templates: Terra Nanotech
from tnnt_templates import urls


@hooks.register("url_hook")
def register_urls():
    """
    Register our urls

    :return:
    :rtype:
    """

    return UrlHook(urls=urls, namespace="tnnt_templates", base_url=r"^tnnt-templates/")
