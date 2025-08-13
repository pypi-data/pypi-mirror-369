import argparse
from .version import VERSION
from .subcommands.enable_user import enable_user
from .subcommands.disable_user import disable_user
from .subcommands.get_mailbox import get_mailbox
from .subcommands.set_property import set_property
from .subcommands.set_password import set_password
from .subcommands.create_login_token import create_login_token
from .subcommands.list_all import search_mailboxes

def main():
    main_parser = argparse.ArgumentParser(prog="rackmail",description="CLI to interact with Rackspace's Hosted Email API",)
    main_parser.add_argument("--version",action="version",version=f"{main_parser.prog} V.{VERSION}")

    # This is store two arguments, we can add this as a parent to sub parsers so they will use the --email and --domain arguments.
    global_command_parser = argparse.ArgumentParser(add_help=False)
    global_command_parser.add_argument("-e","--email",action="store",metavar="email",dest="email",help="the email address of a mailbox",required=True)
    global_command_parser.add_argument("-d","--domain",action="store",metavar="domain",dest="domain",help="the domain of a mailbox",required=True)

    subparsers = main_parser.add_subparsers(title="Commands",dest="command",metavar="")

    enable_user_subcommand = subparsers.add_parser("enableuser",help="Enables a hosted mailbox",parents=[global_command_parser])
    enable_user_subcommand.set_defaults(func=enable_user)

    disable_user_subcommand = subparsers.add_parser("disableuser",help="Disables a hosted mailbox",parents=[global_command_parser])
    disable_user_subcommand.set_defaults(func=disable_user)
    get_mailbox_subcommand = subparsers.add_parser("getmailbox",help="Gets all available information about a mailbox",parents=[global_command_parser])
    get_mailbox_subcommand.set_defaults(func=get_mailbox)

    change_password_subcommand = subparsers.add_parser("setpassword",help="Sets the password of a mailbox",parents=[global_command_parser])
    change_password_subcommand.add_argument("-p","--password",action="store",metavar="password",dest="password",help="The password you want set on a mailbox",required=False,default=None)
    change_password_subcommand.set_defaults(func=set_password)

    token_subcommand = subparsers.add_parser("createlogintoken",help="Creates a login token for a mailbox for SSO or viewing.",parents=[global_command_parser])
    token_subcommand.add_argument("-w","--webmail",help="Your custom webmail address",metavar="webmail_url",dest="webmail_url")
    token_subcommand.set_defaults(func=create_login_token)

    list_subcommand= subparsers.add_parser("listall",help="Lists mailboxes for a domain, under given parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Lists out emails for a domain based on arguments given.\n\n"
            "Arguments:\n"
            " -d,--domain:str [REQUIRED]\n"
            "  The domain your wanting to get data from. Should be in your rackspace tenant\n\n"
            " -f,--fields:str [OPTIONAL](comma seperate list of below fields)\n"
            "   You can add fields as a comma seperated list with -f,--fields\n"
            "   There are 5 available fields listed in Rackspace's documentation\n"
            "   Fields:\n"
            "     size,currentUsage,enabled,createdDate,lastLogin\n\n"
            " -p,--page:int [OPTIONAL]\n"
            "    This will return a specific page\n"
            "    If this argument is NOT present, --output MUST be present"
            "    If you do not know how many pages, run without this argument\n"
            "    Command returns 250 results per page, so divide your total number from 250.\n\n"
            " -o,--output:str [OPTIONAL]\n"
            "    This is the full filepath where you want your list to output.\n"
            "    If you provide this argument, a json will be created in the path provided"
            "    This argument will NOT create a folder, so ensure your folder is real\n\n"
            "Examples:\n"
            "  rackmail listall -d mydomain.com -f currentUsage,enabled,createdDate\n"
            "  rackmail listall -d mydomain.com -p 50\n"
            "  rackmail listall -d mydomain.com -p 50 -f currentUsage,enabled,createdDate\n"
            "  rackmail listall -d mydomain.com -p 50 -f currentUsage,enabled,createdDate\n"
            "  rackmail listall -d mydomain.com -o /var/log/rackmail/output.json\n"
        ),)
    list_subcommand.add_argument("-d","--domain",action="store",metavar="",dest="domain",help="the domain of a mailbox",required=True)
    list_subcommand.add_argument('-f',"--fields",action="store",metavar="",dest="fields",help="Optional comma seperated list of fields you want to output")
    list_subcommand.add_argument("-p","--page",action="store",metavar="",dest="page",help="The page number you want to list")
    list_subcommand.add_argument("-o","--output",action="store",metavar="",dest="output",help="The full filepath where you want your CSV to be created")
    list_subcommand.set_defaults(func=search_mailboxes)

    set_subcommand = subparsers.add_parser(
        "set",
        help="Set any property from the Rackspace API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Set Rackspace API properties that don’t need their own command.\n"
            "Use this for things like BusinessUnit, TimeZone, or other one-off fields.\n\n"
            "Examples:\n"
            "  rackmail set BusinessUnit WaffleOps -e user.name -d mydomain.com\n"
            "  rackmail set TimeZone America/New_York -e user.name -d mydomain.com\n"
        ),
        epilog=(
            "For a list of all possible properties visit RackSpace Hosted Email API Reference\n"
            "http://api-wiki.apps.rackspace.com/api-wiki/index.php/Rackspace_Mailbox_(Rest_API)\n\n"
            "Note: This command does not validate property names or values—use it when you know what you’re doing."
        ),
        parents=[global_command_parser])
    set_subcommand.add_argument("property",action="store",metavar="property",help="The property being changed")
    set_subcommand.add_argument("value",action="store",metavar="value",help="The updated value of the property being changed")
    set_subcommand.set_defaults(func=set_property)
    
    args = main_parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        main_parser.print_help()

if __name__ == "__main__":
    main()