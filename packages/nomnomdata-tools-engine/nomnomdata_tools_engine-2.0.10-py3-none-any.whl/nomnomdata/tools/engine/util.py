import json
import logging
from urllib.parse import urljoin

import click
import requests


class NomitallSession(requests.Session):
    def __init__(self, prefix_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.logger = logging.getLogger("nomitall.session")

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        self.logger.debug(f"Request {method}:{url}")
        resp = super().request(method, url, *args, **kwargs)
        self.check_response(resp)
        return resp

    def check_response(self, resp):
        if not resp.ok:
            try:
                reply_data = resp.json()
                if resp.status_code == 401:
                    self.logger.error(f"Check secret key is valid\n\t\t {reply_data}")
                elif resp.status_code == 403:
                    self.logger.error(f"Check user permissions\n\t\t {reply_data}")
                else:
                    self.logger.error(f"Error from Nomitall: {reply_data}")
            except json.JSONDecodeError:
                self.logger.error(
                    f"Error {resp.status_code} while communicating with nomitall : {resp.text}"
                )
            raise click.Abort
