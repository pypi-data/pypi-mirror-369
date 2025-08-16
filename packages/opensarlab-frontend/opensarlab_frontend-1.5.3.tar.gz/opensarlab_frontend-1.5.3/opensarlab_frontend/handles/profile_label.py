import json
import os

import logging

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

logging.basicConfig(format="%(filename)s %(asctime)s %(message)s")


class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        """
        /opensarlab-frontend/opensarlab-profile-label
        """
        profile_name = os.environ.get("OPENSARLAB_PROFILE_NAME", "")

        if not profile_name:
            logging.warning("Environ variable 'OPENSARLAB_PROFILE_NAME' not found.")

        self.finish(json.dumps({"data": profile_name}))


def setup_handlers(base_url, url_path=None):
    route_pattern = url_path_join(base_url, "opensarlab-profile-label")
    return [(route_pattern, RouteHandler)]
