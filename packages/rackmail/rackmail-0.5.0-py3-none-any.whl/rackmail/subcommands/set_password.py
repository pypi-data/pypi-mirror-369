from ..client import RackspaceClient
from ..utils.generate_random_string import generate_random_string
from ..utils.output_json import output_json
from requests import put

def set_password(args):
    rackspace_client = RackspaceClient()

    if args.password:
        password = args.password
    else:
        password = generate_random_string()

    url = f"https://api.emailsrvr.com/v1/customers/{rackspace_client.customer_id}/domains/{args.domain}/rs/mailboxes/{args.email}"
    request = put(url,headers=RackspaceClient().auth_header,json={"password":password})

    print(
        output_json(
            request.status_code,
            args.command,
            f"{args.email}@{args.domain}",
            {"Password":password} if request.status_code == 200 else request.text)
        )