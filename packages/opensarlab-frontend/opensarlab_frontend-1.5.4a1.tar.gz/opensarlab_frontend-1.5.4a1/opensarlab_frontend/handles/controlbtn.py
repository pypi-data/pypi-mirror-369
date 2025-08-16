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
        /opensarlab-frontend/opensarlab-controlbtn
        """
        lab_short_name = os.environ.get("OPENSCIENCELAB_LAB_SHORT_NAME", "")
        osl_portal_domain = os.environ.get("OPENSCIENCELAB_PORTAL_DOMAIN", "")

        if not lab_short_name:
            logging.warning(
                "Environ variable 'OPENSCIENCELAB_LAB_SHORT_NAME' not found."
            )

        if not osl_portal_domain:
            logging.warning(
                "Environ variable 'OPENSCIENCELAB_PORTAL_DOMAIN' not found."
            )

        if not lab_short_name or not osl_portal_domain:
            self.finish(json.dumps({"data": "/hub/home"}))
            return
        self.finish(
            json.dumps({"data": f"{osl_portal_domain}/lab/{lab_short_name}/hub/home"})
        )


def setup_handlers(base_url, url_path=None):
    route_pattern = url_path_join(base_url, "opensarlab-controlbtn")
    return [(route_pattern, RouteHandler)]
