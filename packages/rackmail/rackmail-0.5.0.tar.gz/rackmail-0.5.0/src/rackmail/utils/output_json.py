import json

def output_json(status:int,command:str,email:str,text) -> str:
    """
    Format a standardized JSON response for Rackmail CLI subcommands.

    Args:
        status (int): HTTP status code returned by the Rackspace API.
        command (str): The name of the CLI subcommand executed.
        email (str): The user email associated with the operation.
        text (str): A human-readable message describing the result.

    Returns:
        str: A JSON-formatted string with the following structure:
            {
              "Command": "<command name>",
              "Email": "<user email>",
              "Status": <HTTP status code>,
              "Result": "Success" | "Failure",
              "Text": "<human-readable result message>"
            }

    Notes:
        - "Result" is derived from the status code: 200 = Success, anything else = Failure.
        - Intended for consistent output parsing in scripts, logs, or integrations.
    """
    
    data = {
        "Command": command,
        "Email": email,
        "Status": status,
        "Result": "Success" if status == 200 else "Failure",
        "Text": text
    }

    return json.dumps(data,indent=2)