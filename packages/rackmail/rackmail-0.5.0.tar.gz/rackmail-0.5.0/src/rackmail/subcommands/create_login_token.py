from ..client import RackspaceClient
from ..utils.output_json import output_json
from requests import post
from os import environ

def create_login_token(args):
    rackspace_client = RackspaceClient()

    url = f"https://api.emailsrvr.com/v1/customers/{rackspace_client.customer_id}/domains/{args.domain}/rs/mailboxes/{args.email}/logintoken"
    request = post(url,headers=RackspaceClient().auth_header)
    response = request.json()

    print(environ.get("RACKSPACE_WEBMAIL_URL"))

    if args.webmail_url or environ.get("RACKSPACE_WEBMAIL_URL"):
        if request.status_code == 200:
            webmail_url_unsanitized = args.webmail_url or environ.get("RACKSPACE_WEBMAIL_URL")
            webmail_url = _strip_protocol_prefix(webmail_url_unsanitized)
            response["desktopUrl"] = f"https://{webmail_url}/mail/src/redirect.php?user_name={args.email}@{args.domain}&emailaddress={args.email}@{args.domain}&sessionID={response.get("token")}"
            response["mobileUrl"] = f"https://{webmail_url}/mobile/login.php?user_name={args.email}@{args.domain}&emailaddress={args.email}@{args.domain}&sessionID={response.get("token")}"
    else:
        response["desktopUrl"] = f"No Webmail URL Found"
        response["mobileUrl"] = f"No Webmail URL Found"

    print(
        output_json(
            request.status_code,
            args.command,
            f"{args.email}@{args.domain}",
            response if request.status_code == 200 else request.text)
        )
    
def _strip_protocol_prefix(webmail_url):
    if "https://" in webmail_url:
        return webmail_url.strip("https://")
    elif "http://" in webmail_url:
        return webmail_url.strip("https://")
    else:
        return webmail_url
