from jupyter_server.utils import url_path_join


def setup_handlers(web_app, url_path=None):
    base_url = web_app.settings["base_url"]
    base_url = url_path_join(base_url, "opensarlab-frontend")
    handlers = []

    # OSL Notify
    from .handles.oslnotify import setup_handlers as setup_oslnotify

    handlers += setup_oslnotify(base_url)

    # Profile Label
    from .handles.profile_label import setup_handlers as setup_profile_label

    handlers += setup_profile_label(base_url)

    # Control Button
    from .handles.controlbtn import setup_handlers as setup_controlbtn

    handlers += setup_controlbtn(base_url)

    # Disk Space label
    from .handles.disk_space import setup_handlers as setup_diskspace

    handlers += setup_diskspace(base_url)

    host_pattern = ".*$"
    web_app.add_handlers(host_pattern, handlers)
