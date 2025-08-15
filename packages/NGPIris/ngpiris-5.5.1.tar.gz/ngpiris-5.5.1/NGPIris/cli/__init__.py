
import click
from click.core import Context
from json import dump
from pathlib import Path
from boto3 import set_stream_logger
from typing import Any, Generator
from bitmath import Byte, TiB
import lazy_table as lt
import sys
import os

from NGPIris.hcp import HCPHandler

def add_trailing_slash(path : str) -> str:
    if not path[-1] == "/":
        path += "/"
    return path

def create_HCPHandler(context : Context) -> HCPHandler:
    # hcp_credentials : str | dict[str, str], debug : bool, transfer_config : str

    if context.parent:
        parent_context = context.parent
    else:
        # Should never happen
        click.echo("Something went wrong with the subcommand and parent command relation", err = True)
        sys.exit(1)
    
    credentials : str | None = parent_context.params.get("credentials")

    if credentials:
        hcp_credentials = credentials
    elif os.environ.get("NGPIRIS_CREDENTIALS_PATH", None):
        hcp_credentials = os.environ["NGPIRIS_CREDENTIALS_PATH"]
    else: 
        endpoint : str = click.prompt(
            "Please enter your tenant endpoint"
        )

        aws_access_key_id : str = click.prompt(
            "Please enter your base64 hashed aws_access_key_id"
        )

        aws_secret_access_key : str = click.prompt(
            "Please enter your md5 hashed aws_secret_access_key",
            hide_input = True,
            confirmation_prompt = True
        )

        hcp_credentials = {
            "endpoint" : endpoint,
            "aws_access_key_id" : aws_access_key_id,
            "aws_secret_access_key" : aws_secret_access_key
        }
    
    debug : bool | None = parent_context.params.get("debug")
    transfer_config : str | None = parent_context.params.get("transfer_config")
    if transfer_config:
        hcp_h = HCPHandler(hcp_credentials, custom_config_path = transfer_config)
    else:    
        hcp_h = HCPHandler(hcp_credentials)
    
    if debug:
        set_stream_logger(name="")
        click.echo(hcp_h.transfer_config.__dict__)
        
    return hcp_h

@click.group()
@click.option(
    "-c", 
    "--credentials", 
    help = "Path to a JSON file with credentials", 
)
@click.option(
    "--debug",
    help = "Get the debug log for running a command",
    is_flag = True
)
@click.option(
    "-tc", 
    "--transfer_config", 
    help = "Path for using a custom transfer config for uploads or downloads", 
)
@click.version_option(package_name = "NGPIris")
@click.pass_context
def cli(context : Context, credentials : str, debug : bool, transfer_config : str):
    """
    NGP Intelligence and Repository Interface Software, IRIS. 
    
    CREDENTIALS refers to the path to the JSON credentials file.
    """

@cli.command(short_help = "This command returns a shell command that sets the `NGPIRIS_CREDENTIALS_PATH` enviroment variable depending on your shell")
@click.argument(
    "credentials_path", 
    required = False
)
@click.option(
    "-s",
    "--shell", 
    type = click.Choice(
        ["bash", "fish", "zsh"],
        case_sensitive = False
    ),
    help = "Allows for selection of shell that the produced command should support",
    default = "bash"
)
@click.pass_context
def shell_env(context : Context, credentials_path : str, shell : str):
    """
    NGP IRIS will look for an enviroment variable called 
    `NGPIRIS_CREDENTIALS_PATH` when authenicating. This command returns a 
    shell command that sets the `NGPIRIS_CREDENTIALS_PATH` enviroment variable 
    depending on your shell. 
    
    NOTE: The enviroment variable will only last for this 
    shell session, but you could set the value of `NGPIRIS_CREDENTIALS_PATH`
    permanently via other commands if you wish to do so. 

    CREDENTIALS PATH is the either absolute or relative path to your credentials 
    JSON file
    """
    if not credentials_path:
        click.prompt("Please enter the path to your credentials file")
    
    click.echo("Copy and paste the following command in order to set your environment variable:")
    match shell:
        case "bash":
            click.echo("export NGPIRIS_CREDENTIALS_PATH=" + credentials_path)
        case "fish":
            click.echo("set -x NGPIRIS_CREDENTIALS_PATH " + credentials_path)
        case "zsh":
            click.echo("export NGPIRIS_CREDENTIALS_PATH=" + credentials_path)

@cli.command()
@click.argument("bucket")
@click.argument("source")
@click.argument("destination")
@click.option(
    "-dr", 
    "--dry_run", 
    help = "Simulate the command execution without making actual changes. Useful for testing and verification", 
    is_flag = True
)
@click.option(
    "-um", 
    "--upload_mode", 
    help = "Choose an upload method. Default upload mode is STANDARD which uses a basic multipart upload. Use another mode than STANDARD if that mode misbehaves",
    type = click.Choice(
        ["STANDARD", "SIMPLE", "EQUAL_PARTS"],
        case_sensitive = False
    ),
    default = "STANDARD"
)
@click.option(
    "-ep", 
    "--equal_parts", 
    help = "Supplementary option when using the EQUAL_PARTS upload mode. Splits each file into a given number of parts. Must be a positive integer", 
    type = int,
    default = 5
)
@click.pass_context
def upload(context : Context, bucket : str, source : str, destination : str, dry_run : bool, upload_mode : str, equal_parts : int):
    """
    Upload files to an HCP bucket/namespace. 
    
    BUCKET is the name of the upload destination bucket.

    SOURCE is the path to the file or folder of files to be uploaded.
    
    DESTINATION is the destination path on the HCP. 
    """

    if equal_parts <= 0:
        click.echo("Error: --equal_parts value must be a positive integer", err=True)
        sys.exit(1)
    
    upload_mode_choice = HCPHandler.UploadMode(upload_mode.lower())

    hcph : HCPHandler = create_HCPHandler(context)
    hcph.mount_bucket(bucket)
    destination = add_trailing_slash(destination)
    if Path(source).is_dir():
        source = add_trailing_slash(source)
        if dry_run:
            click.echo("This command would have uploaded the folder \"" + source + "\" to \"" + destination + "\"")
        else:
            hcph.upload_folder(source, destination, upload_mode = upload_mode_choice, equal_parts = equal_parts)
    else:
        file_name = Path(source).name
        destination += file_name
        if dry_run:
            click.echo("This command would have uploaded the file \"" + source + "\" to \"" + destination + "\"")
        else:
            hcph.upload_file(source, destination, upload_mode = upload_mode_choice, equal_parts = equal_parts)

@cli.command(short_help = "Download a file or folder from an HCP bucket/namespace.")
@click.argument("bucket")
@click.argument("source")
@click.argument("destination")
@click.option(
    "-f", 
    "--force", 
    help = "Overwrite existing file with the same name (single file download only)", 
    is_flag = True
)
@click.option(
    "-iw", 
    "--ignore_warning", 
    help = "Ignore the download limit", 
    is_flag = True
)
@click.option(
    "-dr", 
    "--dry_run", 
    help = "Simulate the command execution without making actual changes. Useful for testing and verification", 
    is_flag = True
)
@click.pass_context
def download(context : Context, bucket : str, source : str, destination : str, force : bool, ignore_warning : bool, dry_run : bool):
    """
    Download a file or folder from an HCP bucket/namespace.

    BUCKET is the name of the download source bucket.

    SOURCE is the path to the object or object folder to be downloaded.

    DESTINATION is the folder where the downloaded object or object folder is to be stored locally. 
    """
    def object_is_folder(object_path : str, hcph : HCPHandler) -> bool:
        return (object_path[-1] == "/") and (hcph.get_object(object_path)["ContentLength"] == 0)
        
    hcph : HCPHandler = create_HCPHandler(context)
    hcph.mount_bucket(bucket)
    if not Path(destination).exists():
        Path(destination).mkdir()

    if not dry_run:
        if object_is_folder(source, hcph):
            if source == "/":
                source = ""

            cumulative_download_size = Byte(0)
            if not ignore_warning:
                click.echo("Computing download size...")
                for object in hcph.list_objects(source):
                    object : dict
                    cumulative_download_size += Byte(object["Size"])
                    if cumulative_download_size >= TiB(1):
                        click.echo("WARNING: You are about to download more than 1 TB of data. Is this your intention? [y/N]: ", nl = False)
                        inp = click.getchar(True)
                        if inp == "y" or inp == "Y":
                            break
                        else: # inp == "n" or inp == "N" or something else
                            exit("\nAborting download")
        
            hcph.download_folder(source, Path(destination).as_posix())
        else: 
            if Byte(hcph.get_object(source)["ContentLength"]) >= TiB(1):
                click.echo("WARNING: You are about to download more than 1 TB of data. Is this your intention? [y/N]: ", nl = False)
                inp = click.getchar(True)
                if inp == "y" or inp == "Y":
                    pass
                else: # inp == "n" or inp == "N" or something else
                    exit("\nAborting download")

            downloaded_source = Path(destination) / Path(source).name
            if downloaded_source.exists() and not force:
                exit("Object already exists. If you wish to overwrite the existing file, use the -f, --force option")
            hcph.download_file(source, downloaded_source.as_posix())
    else: 
        if object_is_folder(source, hcph):
            click.echo("This command would have downloaded the folder \"" + source + "\". If you wish to know the contents of this folder, use the 'list-objects' command")
        else:
            click.echo("This command would have downloaded the object \"" + source + "\":")
            click.echo(list(hcph.list_objects(source))[0])

@cli.command()
@click.argument("bucket")
@click.argument("object")
@click.option(
    "-dr", 
    "--dry_run", 
    help = "Simulate the command execution without making actual changes. Useful for testing and verification", 
    is_flag = True
)
@click.pass_context
def delete_object(context : Context, bucket : str, object : str, dry_run : bool):
    """
    Delete an object from an HCP bucket/namespace. 

    BUCKET is the name of the bucket where the object to be deleted exist.

    OBJECT is the name of the object to be deleted.
    """
    hcph : HCPHandler = create_HCPHandler(context)
    hcph.mount_bucket(bucket)
    if not dry_run:
        click.echo(hcph.delete_object(object))
    else: 
        click.echo("This command would delete:")
        click.echo(list(hcph.list_objects(object))[0])

@cli.command()
@click.argument("bucket")
@click.argument("folder")
@click.option(
    "-dr", 
    "--dry_run", 
    help = "Simulate the command execution without making actual changes. Useful for testing and verification", 
    is_flag = True
)
@click.pass_context
def delete_folder(context : Context, bucket : str, folder : str, dry_run : bool):
    """
    Delete a folder from an HCP bucket/namespace. 

    BUCKET is the name of the bucket where the folder to be deleted exist.

    FOLDER is the name of the folder to be deleted.
    """
    hcph : HCPHandler = create_HCPHandler(context)
    hcph.mount_bucket(bucket)
    if not dry_run:
        click.echo(hcph.delete_folder(folder))
    else:
        click.echo("By deleting \"" + folder + "\", the following objects would have been deleted (not including objects in sub-folders):")
        for obj in hcph.list_objects(folder):
            click.echo(obj)

@cli.command()
@click.argument("bucket")
@click.option(
    "-dr", 
    "--dry_run", 
    help = "Simulate the command execution without making actual changes. Useful for testing and verification", 
    is_flag = True
)
@click.pass_context
def delete_bucket(context : Context, bucket : str, dry_run : bool):
    hcph : HCPHandler = create_HCPHandler(context)
    if not dry_run:
        click.echo(hcph.delete_bucket(bucket))
    else:
        click.echo("This command would have deleted the bucket called \"" + bucket + "\"")

@cli.command()
@click.pass_context
def list_buckets(context : Context):
    """
    List the available buckets/namespaces on the HCP.
    """
    hcph : HCPHandler = create_HCPHandler(context)
    click.echo(
        "".join(
            list(map(lambda s : s + "\n", hcph.list_buckets()))
        ).strip("\n")
    )

@cli.command(short_help = "List the objects in a certain bucket/namespace on the HCP.")
@click.argument("bucket")
@click.argument("path", required = False)
@click.option(
    "-p",
    "--pagination",
    help = "Output as a paginator",
    default = False,
    is_flag = True
)
@click.option(
    "-fo", 
    "--files-only", 
    help = "Output only file objects", 
    default = False,
    is_flag = True
)
@click.option(
    "-e", 
    "--extended-information", 
    help = "Output the fully exteded information for each object", 
    default = False,
    is_flag = True
)
@click.pass_context
def list_objects(context : Context, bucket : str, path : str, pagination : bool, files_only : bool, extended_information : bool):
    """
    List the objects in a certain bucket/namespace on the HCP.

    BUCKET is the name of the bucket in which to list its objects.

    PATH is an optional argument for where to list the objects
    """
    def list_objects_generator(hcph : HCPHandler, path : str, files_only : bool, output_mode : HCPHandler.ListObjectsOutputMode) -> Generator[str, Any, None]:
        """
        Handle object list as a paginator that `click` can handle. It works slightly 
        different from `list_objects` in `hcp.py` in order to make the output 
        printable in a terminal
        """
        objects = hcph.list_objects(path, output_mode = output_mode, files_only = files_only)
        for obj in objects:
            yield str(obj) + "\n"

    hcph : HCPHandler = create_HCPHandler(context)
    hcph.mount_bucket(bucket)
    output_mode = (
        HCPHandler.ListObjectsOutputMode.EXTENDED if extended_information 
        else HCPHandler.ListObjectsOutputMode.SIMPLE
    )

    if path:
        path_with_slash = add_trailing_slash(path)

        if not hcph.object_exists(path_with_slash):
            raise RuntimeError("Path does not exist")
    else:
        path_with_slash = ""

    if pagination:
        click.echo_via_pager(
            list_objects_generator(
                hcph, 
                path_with_slash, 
                files_only, 
                output_mode
            )
        )
    else:
        lt.stream(
            hcph.list_objects(
                path_with_slash, 
                output_mode = output_mode,
                files_only = files_only
            ),
            headers = "keys"
        )

@cli.command(short_help = "Make simple search using substrings in a bucket/namespace on the HCP.")
@click.argument("bucket")
@click.argument("search_string")
@click.option(
    "-cs", 
    "--case_sensitive", 
    help = "Use case sensitivity? Default value is False", 
    default = False,
    is_flag = True
)
@click.pass_context
def simple_search(context : Context, bucket : str, search_string : str, case_sensitive : bool):
    """
    Make simple search using substrings in a bucket/namespace on the HCP.

    NOTE: This command does not use the HCI. Instead, it uses a linear search of 
    all the objects in the HCP. As such, this search might be slow.

    BUCKET is the name of the bucket in which to make the search.

    SEARCH_STRING is any string that is to be used for the search.
    """
    hcph : HCPHandler = create_HCPHandler(context)
    hcph.mount_bucket(bucket)
    list_of_results = hcph.search_in_bucket(
        search_string,  
        case_sensitive = case_sensitive
    )
    click.echo("Search results:")
    lt.stream(
        list_of_results,
        headers = "keys"
    )

@cli.command(short_help = "Make a fuzzy search using a search string in a bucket/namespace on the HCP.")
@click.argument("bucket")
@click.argument("search_string")
@click.option(
    "-cs", 
    "--case_sensitive", 
    help = "Use case sensitivity? Default value is False", 
    default = False,
    is_flag = True
)
@click.option(
    "-t", 
    "--threshold", 
    help = "Set the threshold for the fuzzy search score. Default value is 80", 
    default = 80
)
@click.pass_context
def fuzzy_search(context : Context, bucket : str, search_string : str, case_sensitive : bool, threshold : int):
    """
    Make a fuzzy search using a search string in a bucket/namespace on the HCP.

    NOTE: This command does not use the HCI. Instead, it uses the RapidFuzz 
    library in order to find objects in the HCP. As such, this search might be 
    slow.

    BUCKET is the name of the bucket in which to make the search.

    SEARCH_STRING is any string that is to be used for the search.
    """
    hcph : HCPHandler = create_HCPHandler(context)
    hcph.mount_bucket(bucket)
    list_of_results = hcph.fuzzy_search_in_bucket(
        search_string, 
        case_sensitive = case_sensitive,
        threshold = threshold
    ) 
    click.echo("Search results:")
    lt.stream(
        list_of_results,
        headers = "keys"
    )

@cli.command()
@click.argument("bucket")
@click.pass_context
def test_connection(context : Context, bucket : str):
    """
    Test the connection to a bucket/namespace.

    BUCKET is the name of the bucket for which a connection test should be made.
    """
    hcph : HCPHandler = create_HCPHandler(context)
    click.echo(hcph.test_connection(bucket))

@click.command()
@click.option(
    "--path",
    help = "Path for where to put the new credentials file.",
    default = ""
)
@click.option(
    "--name",
    help = "Custom name for the credentials file. Will filter out everything after a \".\" character, if any exist.",
    default = "credentials"
)
def iris_generate_credentials_file(path : str, name : str):
    """
    Generate blank credentials file for the HCI and HCP. 

    WARNING: This file will store sensitive information (such as passwords) in plaintext.
    """
    credentials_dict = {
        "hcp" : {
            "endpoint" : "",
            "aws_access_key_id" : "",
            "aws_secret_access_key" : ""
        },
        "hci" : {
            "username" : "",
            "password" : "",
            "address" : "",
            "auth_port" : "",
            "api_port" : ""
        }
    }

    name = name.split(".")[0] + ".json"
    if path:
        if not path[-1] == "/":
            path += "/"

        if path == ".":
            file_path = name    
        else:
            file_path = path + name
    
        if not Path(path).is_dir():
            Path(path).mkdir(parents=True)
    else:
        file_path = name
        
    with open(file_path, "w") as f:
        dump(credentials_dict, f, indent = 4)
