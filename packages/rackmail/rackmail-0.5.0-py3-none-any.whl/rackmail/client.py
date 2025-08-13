from os import environ
from dotenv import load_dotenv,find_dotenv
from .version import VERSION

class RackspaceClient():
    def __init__(self,api_header=None,customer_id=None) -> None:
        load_dotenv()
        self.api_header = api_header or environ.get("RACKSPACE_API_HEADER")
        self.customer_id = customer_id or environ.get("RACKSPACE_CUSTOMER_ID")
        self.auth_header = None

        if self.api_header == None:
            raise EnvironmentError("Missing environment variable RACKSPACE_API_HEADER")
        if self.customer_id == None:
            raise EnvironmentError("Missing environment variable RACKSPACE_CUSTOMER_ID")

        self.set_header()

    def set_header(self):
        self.auth_header = {"X-Api-Signature": f"{self.api_header}","User-Agent":"rackmailcli","Accept":"application/json"}