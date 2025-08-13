from ..client import RackspaceClient
from ..utils.output_json import output_json
from requests import get

def get_mailbox(args):
    rackspace_client = RackspaceClient()

    url = f"https://api.emailsrvr.com/v1/customers/{rackspace_client.customer_id}/domains/{args.domain}/rs/mailboxes/{args.email}"
    request = get(url,headers=RackspaceClient().auth_header)

    print(
        output_json(
            request.status_code,
            args.command,
            f"{args.email}@{args.domain}",
            request.json() if request.status_code == 200 else request.text)
        )