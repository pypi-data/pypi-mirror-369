c = get_config()  # noqa

# load base config
load_subconfig("/etc/jupyter/jupyter_server_config_base.py")  # noqa

# supports iframe and samesite cookies
c.ServerApp.tornado_settings = {
    "headers": {"Content-Security-Policy": "frame-ancestors 'self' *"},
    "cookie_options": {"SameSite": "None", "Secure": True},
}
c.ServerApp.allow_root = True
c.ServerApp.allow_origin = "*"

c.IdentityProvider.token = ""
# c.ServerApp.default_url = "/lab"
