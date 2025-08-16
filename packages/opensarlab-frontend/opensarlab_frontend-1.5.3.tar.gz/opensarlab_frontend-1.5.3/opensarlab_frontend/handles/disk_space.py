import json
import logging
import shutil

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
        /opensarlab-frontend/opensarlab-diskspace
        """

        try:
            disk_space_path = self.get_query_argument("path")

            total, used, free = shutil.disk_usage(disk_space_path)

            self.finish(
                json.dumps({"data": {"total": total, "used": used, "free": free}})
            )

        except FileNotFoundError:
            logging.error(
                f"Path '{disk_space_path}' not found. Cannot get disk space usage."
            )
            exit

        except Exception as e:
            logging.error(f"Cannot handle error: {e}")


def setup_handlers(base_url, url_path=None):
    route_pattern = url_path_join(base_url, "opensarlab-diskspace")
    return [(route_pattern, RouteHandler)]
