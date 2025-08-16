import shutil
import pathlib


def main(df_path: pathlib.Path = pathlib.Path.home()):
    try:
        active_events = []

        # Get storage usage
        res = shutil.disk_usage(df_path)

        GB = 1.0 / 1024 / 1024 / 1024
        storage_usage = f"{res.used * GB:.2f}"
        storage_total = f"{res.total * GB:.2f}"
        # storage_free = f"{res.free * GB:.2f}"
        storage_percent = f"{res.used / res.total * 100.0:.2f}"
        storage_percent_raw = res.used / res.total * 100.0

        event_name = "Current Storage Usage"
        if storage_percent_raw > 99:
            event_type = "error"
            severity = 1
            message = f"""
                <h1>Current storage usage is at {storage_percent}% ({storage_usage} / {storage_total} GB).</h1>
                <h2>Please delete any unused files. Failure to do so may make your server unresponsive.</h2>
            """

        elif storage_percent_raw > 90:
            event_type = "warning"
            severity = 0
            message = f"<p>Current storage usage is at {storage_percent}% ({storage_usage} / {storage_total} GB)</p>"

        else:
            event_type = "success"
            severity = 0
            message = f"<p>Current storage usage is at {storage_percent}% ({storage_usage} / {storage_total} GB)</p>"

        active_events.append(
            {
                "title": event_name,
                "message": message,
                "type": event_type,
                "severity": severity,
            }
        )

        return active_events

    except Exception as e:
        print(e)
        raise Exception(f"{e}")
