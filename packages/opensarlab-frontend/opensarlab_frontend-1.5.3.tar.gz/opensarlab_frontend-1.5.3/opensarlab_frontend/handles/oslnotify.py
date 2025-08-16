import json
import os
import logging

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

from .oslnotify_lib import calendar
from .oslnotify_lib import storage

logging.basicConfig(format="%(filename)s %(asctime)s %(message)s")


class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        """
        /opensarlab-frontend/opensarlab-oslnotify?type=calendar,storage
        """
        note_type = self.get_query_argument("type")
        note_type = note_type.split(",")

        profile_name = os.environ.get("OPENSARLAB_PROFILE_NAME", "")
        lab_short_name = os.environ.get("OPENSCIENCELAB_LAB_SHORT_NAME", "")
        portal_domain = os.environ.get("OPENSCIENCELAB_PORTAL_DOMAIN", "")

        if not profile_name:
            logging.warning("Environ variable 'OPENSARLAB_PROFILE_NAME' not found.")

        if not lab_short_name:
            logging.warning(
                "Environ variable 'OPENSCIENCELAB_LAB_SHORT_NAME' not found."
            )

        if not portal_domain:
            logging.warning(
                "Environ variable 'OPENSCIENCELAB_PORTAL_DOMAIN' not found."
            )

        events = []

        if "calendar" in note_type:
            events += calendar.main(profile_name, lab_short_name, portal_domain)

        if "storage" in note_type:
            events += storage.main()

        options = {
            "closeButton": "true",
            "newestOnTop": "true",
            "progressBar": "true",
            "positionClass": "toast-bottom-right",
            "preventDuplicates": "false",
            "onclick": "false",
            "showDuration": "30",
            "hideDuration": "1",
            "timeOut": "0",
            "extendedTimeOut": "0",
            "showEasing": "swing",
            "hideEasing": "linear",
            "showMethod": "fadeIn",
            "hideMethod": "fadeOut",
        }

        if any([e.get("severity", "-1") for e in events]) == 1:
            options["positionClass"] = "toast-top-full-width"

        self.finish(json.dumps({"data": events, "options": options}))


def setup_handlers(base_url, url_path=None):
    route_pattern = url_path_join(base_url, "opensarlab-oslnotify")
    return [(route_pattern, RouteHandler)]
