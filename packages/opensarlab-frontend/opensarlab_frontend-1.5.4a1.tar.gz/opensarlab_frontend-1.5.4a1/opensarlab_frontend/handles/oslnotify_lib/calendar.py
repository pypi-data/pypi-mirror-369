import requests


def main(
    profile_name: str = "default",
    lab_short_name: str = "default",
    portal_domain: str = "https://example.com",
):
    try:
        active_events = []

        # Get calendar notifications
        resp = requests.get(
            f"{portal_domain}/user/notifications/{lab_short_name}?profile={profile_name}"
        )
        resp = resp.json()

        for event in resp:
            type_event = event.get("type", "success")
            if type_event == "error":
                severity = 1
            else:
                severity = 0

            active_events.append(
                {
                    "title": event.get("title", "Notification"),
                    "message": event.get("message", ""),
                    "type": type_event,
                    "severity": severity,
                }
            )

        return active_events

    except requests.exceptions.MissingSchema as e:
        print(e)
        return []

    except Exception as e:
        print(e)
        raise Exception(f"{e}")
