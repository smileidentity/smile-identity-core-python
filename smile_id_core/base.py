"""Constains reusable functions across this repository."""
from typing import Union

from smile_id_core import constants


class Base:
    """A super class that defines reusable constructor variables."""

    def __init__(
        self, partner_id: str, api_key: str, sid_server: Union[str, int]
    ):
        """Initialize all relevant params required for job submission/query.

        argument(s):
        partner_id (str): Smile partner id from the portal
        api_key (str): Api key from the portal
        sid_server (str/int): The server to use for the SID API. 0 for staging
            and 1 for production.
        """
        if not partner_id or not api_key:
            raise ValueError("partner_id or api_key cannot be null or empty")
        self.partner_id = partner_id
        self.api_key = api_key
        self.sid_server = sid_server
        if sid_server in [0, 1, "0", "1"]:
            self.url = constants.sid_server_map[int(sid_server)]
        else:
            self.url = str(sid_server)
