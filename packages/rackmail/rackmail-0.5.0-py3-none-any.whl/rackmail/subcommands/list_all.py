from ..client import RackspaceClient
from ..utils.output_json import output_json
from requests import get
from math import ceil
from json import dump,dumps

def search_mailboxes(args):
    rackspace_client = RackspaceClient()

    url = f"https://api.emailsrvr.com/v1/customers/{rackspace_client.customer_id}/domains/{args.domain}/rs/mailboxes?size=250"

    if args.fields:
        field_list = args.fields.split()
        if not isinstance(field_list,list):
            raise TypeError("Fields argument was not input correctly. Please make sure its a comma separated list.\n-f size,currentUsage,enabled,createdDate")
        else:
            url = url + f"&fields={args.fields}"

    if args.page:
        url = url + f"&offset={args.page}"
        request = get(url,headers=RackspaceClient().auth_header)
        print(
            output_json(
                request.status_code,
                args.command,
                f"{args.domain}",
                request.json() if request.status_code == 200 else request.text)
            )

    elif args.output:
        request = get(url,headers=RackspaceClient().auth_header)
        json_serialized_request = request.json()
        total_emails = int(json_serialized_request.get("total"))
        page_size = 250
        total_email_list = []

        if total_emails < page_size:
            mailbox_list = json_serialized_request.get("rsMailboxes")
            for mailbox in mailbox_list:
                total_email_list.append(mailbox)
            try:
                with open(args.output,"w") as file:
                    dump(total_email_list,file,indent=2)
                print(
                    output_json(
                    200,
                    args.command,
                    f"{args.domain}",
                    f"Your file has been created at {args.output}"
                    )
                )
            except Exception as e:
                print(
                    output_json(
                        500,
                        args.command,
                        f"{args.domain}",
                        f"{e}"
                    )
                )
        else:
            total_pages = ceil(total_emails / page_size)
            page_list = _get_all_page_urls(total_pages,url)

            for page in page_list:
                request = get(page,headers=RackspaceClient().auth_header)
                response = request.json()
                mailbox_list = response.get("rsMailboxes")
                for mailbox in mailbox_list:
                    total_email_list.append(mailbox)
            try:
                with open(args.output,"w") as file:
                    dump(total_email_list,file,indent=2)

                print(
                    output_json(
                    200,
                    args.command,
                    f"{args.domain}",
                    f"Your file has been created at {args.output}"
                    )
                )
            except Exception as e:
                print(
                    output_json(
                        500,
                        args.command,
                        f"{args.domain}",
                        f"{e}"
                    )
                )

def _get_all_page_urls(total_pages,url) -> list:
    page_list = []
    offset = 0
    for i in range(total_pages):
        page_url = url + f"&offset={offset}"
        offset += 250
        page_list.append(page_url)

    return page_list