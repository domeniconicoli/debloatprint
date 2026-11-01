"""Floor of printer settings a profile is not allowed to turn off."""

FLOOR = frozenset(
    {
        "wifi0",
        "infrastructure-wifi",
        "ipp",
        "airprint",
        "bonjour",
        "mdns",
        "dhcp",
        "ipv4",
    }
)


class Refused(Exception):
    def __init__(self, change_id: str):
        self.change_id = change_id
        super().__init__(
            f"refusing to touch {change_id}: the printer needs it to stay reachable"
        )


def assert_allowed(change_id: str, extra_never_touch=()) -> None:
    """Refuse a change that would take printing or the home network away.

    A profile may add names to the block list. It cannot remove the floor.
    """
    blocked = set(FLOOR)
    blocked.update(str(name).strip().lower() for name in extra_never_touch)
    key = str(change_id).strip().lower()
    if key in blocked:
        raise Refused(key)
