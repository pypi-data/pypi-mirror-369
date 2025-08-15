from NGPIris.parse_credentials import CredentialsHandler
from NGPIris.hcp.helpers import (
    raise_path_error,
    create_access_control_policy,
    check_mounted
)
from NGPIris.hcp.exceptions import (
    VPNConnectionError,
    BucketNotFound,
    BucketForbidden,
    ObjectAlreadyExist,
    ObjectDoesNotExist,
    DownloadLimitReached,
    NotADirectory
)

from boto3 import client
from botocore.client import Config
from botocore.paginate import PageIterator, Paginator
from botocore.exceptions import EndpointConnectionError, ClientError
from boto3.s3.transfer import TransferConfig
from configparser import ConfigParser
from pathlib import Path
from itertools import islice
from more_itertools import peekable

from os import (
    stat,
    listdir
)
from json import dumps
from parse import (
    parse,
    Result
)
from rapidfuzz import (
    fuzz,
    process, 
    utils
)
from requests import get
from urllib3 import disable_warnings
from tqdm import tqdm
from bitmath import TiB, Byte

from enum import Enum
from typing import Any, Generator

_KB = 1024
_MB = _KB * _KB

class HCPHandler:
    def __init__(self, credentials : str | dict[str, str], use_ssl : bool = False, proxy_path : str = "", custom_config_path : str = "") -> None:       
        """
        Class for handling HCP requests.

        :param credentials: If `credentials` is a `str`, then it will be interpreted as a path to the JSON credentials file. If `credentials` is a `dict`, then a dictionary with the appropriate HCP credentials is expected: ```{"endpoint" : "", "aws_access_key_id" : "", "aws_secret_access_key" : "" }```
        :type credentials: str | dict
        
        :param use_ssl: Boolean choice between using SSL, defaults to False
        :type use_ssl: bool, optional
        
        :param custom_config_path: Path to a .ini file for customs settings regarding download and upload
        :type custom_config_path: str, optional
        """
        if type(credentials) is str:
            credentials_handler = CredentialsHandler(credentials)
            self.hcp = credentials_handler.hcp
            
            self.endpoint = "https://" + self.hcp["endpoint"]
            self.aws_access_key_id = self.hcp["aws_access_key_id"]
            self.aws_secret_access_key = self.hcp["aws_secret_access_key"]
        elif type(credentials) is dict:
            self.endpoint = "https://" + credentials["endpoint"]
            self.aws_access_key_id = credentials["aws_access_key_id"]
            self.aws_secret_access_key = credentials["aws_secret_access_key"]


        # A lookup table for GMC names to HCP tenant names
        gmc_tenant_map = {
            "gmc-joint" : "vgtn0008",
            "gmc-west" : "vgtn0012",
            "gmc-southeast" : "vgtn0014",
            "gmc-south" : "vgtn0015",
            "gmc-orebro" : "vgtn0016",
            "gmc-karolinska" : "vgtn0017",
            "gmc-north" : "vgtn0018",
            "gmc-uppsala" : "vgtn0019"
        }

        self.tenant = None
        for endpoint_format_string in ["https://{}.ngp-fs1000.vgregion.se", "https://{}.ngp-fs2000.vgregion.se", "https://{}.ngp-fs3000.vgregion.se", "https://{}.hcp1.vgregion.se", "https://{}.vgregion.sjunet.org"]:
            tenant_parse = parse(endpoint_format_string, self.endpoint) 
            if type(tenant_parse) is Result:
                tenant = str(tenant_parse[0])
                if endpoint_format_string == "https://{}.vgregion.sjunet.org": # Check if endpoint is Sjunet
                    mapped_tenant = gmc_tenant_map.get(tenant)
                    if mapped_tenant:
                        self.tenant = mapped_tenant
                    else:
                        raise RuntimeError("The provided tenant name, \"" + tenant + "\", could is not a valid tenant name. Hint: did you spell it correctly?")
                else:
                    self.tenant = tenant
                
                break
        

        if not self.tenant:
            raise RuntimeError("Unable to parse endpoint, \"" + self.endpoint + "\". Make sure that you have entered the correct endpoint in your credentials JSON file. Hints:\n - The endpoint should *not* contain \"https://\" or port numbers\n - Is the endpoint spelled correctly?")
        self.base_request_url = self.endpoint + ":9090/mapi/tenants/" + self.tenant
        self.token = self.aws_access_key_id + ":" + self.aws_secret_access_key
        self.bucket_name = None
        self.use_ssl = use_ssl

        if not self.use_ssl:
            disable_warnings()

        if proxy_path: # pragma: no cover
            s3_config = Config(
                s3 = {
                    "addressing_style": "path",
                    "payload_signing_enabled": True
                },
                signature_version = "s3v4",
                proxies = CredentialsHandler(proxy_path).hcp
            )
        else:
            s3_config = Config(
                s3 = {
                    "addressing_style": "path",
                    "payload_signing_enabled": True
                },
                signature_version = "s3v4"
            )

        self.s3_client = client(
            "s3", 
            aws_access_key_id = self.aws_access_key_id, 
            aws_secret_access_key = self.aws_secret_access_key,
            endpoint_url = self.endpoint,
            verify = self.use_ssl,
            config = s3_config
        )

        if custom_config_path: # pragma: no cover
            ini_config = ConfigParser()
            ini_config.read(custom_config_path)

            self.transfer_config = TransferConfig(
                multipart_threshold = ini_config.getint("hcp", "multipart_threshold"),
                max_concurrency = ini_config.getint("hcp", "max_concurrency"),
                multipart_chunksize = ini_config.getint("hcp", "multipart_chunksize"),
                use_threads = ini_config.getboolean("hcp", "use_threads")
            )
        else:
            self.transfer_config = TransferConfig(
                multipart_threshold = 10 * _MB,
                max_concurrency = 30,
                multipart_chunksize = 40 * _MB,
                use_threads = True
            )
    
    def get_response(self, path_extension : str = "") -> dict:
        """
        Make a request to the HCP in order to use the builtin MAPI

        :param path_extension: Extension for the base request URL, defaults to the empty string
        :type path_extension: str, optional
        :return: The response as a dictionary
        :rtype: dict
        """
        url = self.base_request_url + path_extension
        headers = {
            "Authorization": "HCP " + self.token,
            "Cookie": "hcp-ns-auth=" + self.token,
            "Accept": "application/json"
        }
        response = get(
            url, 
            headers=headers,
            verify=self.use_ssl
        )

        response.raise_for_status()

        return dict(response.json())

    def test_connection(self, bucket_name : str = "") -> dict:
        """
        Test the connection to the mounted bucket or another bucket which is 
        supplied as the argument :py:obj:`bucket_name`.

        :param bucket_name: The name of the bucket to be mounted. Defaults to the empty string
        :type bucket_name: str, optional

        :raises RuntimeError: If no bucket is selected
        :raises VPNConnectionError: If there is no VPN connection
        :raises BucketNotFound: If no bucket of that name was found
        :raises Exception: Other exceptions

        :return: A dictionary of the response
        :rtype: dict
        """
        if not bucket_name and self.bucket_name:
            bucket_name = self.bucket_name
        elif bucket_name:
            pass
        else:
            raise RuntimeError("No bucket selected. Either use `mount_bucket` first or supply the optional `bucket_name` parameter for `test_connection`")
        
        response = {}
        try:
            response = dict(self.s3_client.head_bucket(Bucket = bucket_name))
        except EndpointConnectionError as e: # pragma: no cover
            raise e
        except ClientError as e:
            status_code = e.response["ResponseMetadata"].get("HTTPStatusCode", -1)
            match status_code:
                case 404:
                    raise BucketNotFound("Bucket \"" + bucket_name + "\" was not found")
                case 403:
                    raise BucketForbidden("Bucket \"" + bucket_name + "\" could not be accessed due to lack of permissions")
        except Exception as e: # pragma: no cover
            raise Exception(e)
            
        return response
        
    def mount_bucket(self, bucket_name : str) -> None:
        """
        Mount bucket that is to be used. This method needs to executed in order 
        for most of the other methods to work. It mainly concerns operations with 
        download and upload. 

        :param bucket_name: The name of the bucket to be mounted
        :type bucket_name: str
        """

        # Check if bucket exist
        self.test_connection(bucket_name = bucket_name)
        self.bucket_name = bucket_name

    def create_bucket(self, bucket_name : str) -> None:
        """
        Create a bucket. The user in the given credentials will be the owner 
        of the bucket

        :param bucket_name: Name of the new bucket
        :type bucket_name: str
        """
        self.s3_client.create_bucket(
            Bucket = bucket_name
        )

    def list_buckets(self) -> list[str]:
        """
        List all available buckets at endpoint.

        :return: A list of buckets
        :rtype: list[str]
        """
        
        response = self.get_response("/namespaces")
        list_of_buckets : list[str] = response["name"]
        return list_of_buckets

    class ListObjectsOutputMode(Enum):
        SIMPLE = "simple"
        EXTENDED = "extended"
        NAME_ONLY = "name_only"

    @check_mounted
    def list_objects(
        self, 
        path_key : str = "", 
        output_mode : ListObjectsOutputMode = ListObjectsOutputMode.EXTENDED,
        files_only : bool = False,
        list_all_bucket_objects : bool = False
    ) -> Generator[dict[str, Any], Any, None]:
        """
        List all objects in the mounted bucket as a generator. If one wishes to 
        get the result as a list, use :py:function:`list` to type cast the generator

        :param path_key: Filter string for which keys to list, specifically for finding objects in certain folders. Defaults to \"the root\" of the bucket
        :type path_key: str, optional
        :param output_mode: 
            The upload mode of the transfer is any of the following:\n
                    HCPHandler.ListObjectsOutputMode.SIMPLE,\n
                    HCPHandler.ListObjectsOutputMode.EXTENDED,\n
                    HCPHandler.ListObjectsOutputMode.NAME_ONLY\n
            Default is EXTENDED
        :type output_mode: ListObjectsOutputMode, optional
        :param files_only: If True, only yield file objects. Defaults to False
        :type files_only: bool, optional
        :param list_all_bucket_objects: If True, the value of `path_key` will be ignored and instead will list all objects in the bucket. Defaults to False
        :type list_all_bucket_objects: bool, optional
        :yield: A generator of all objects in specified folder in a bucket
        :rtype: Generator
        """
        paginator : Paginator = self.s3_client.get_paginator("list_objects_v2")
        if list_all_bucket_objects:
            pages : PageIterator = paginator.paginate(Bucket = self.bucket_name)
        else:
            pages : PageIterator = paginator.paginate(Bucket = self.bucket_name, Prefix = path_key, Delimiter = "/")

        for page in pages:
            page : dict | None
            # Check if `page` is None
            if not page:
                break

            if not files_only: # Hide folder objects when flag `files_only` is True
                # Handle folder objects before file objects
                for folder_object in page.get("CommonPrefixes", []):
                    folder_object : dict
                    folder_object_metadata = self.get_object(folder_object["Prefix"])
                    match output_mode:
                        case HCPHandler.ListObjectsOutputMode.EXTENDED:
                            yield {
                                "Key" : folder_object["Prefix"],
                                "LastModified" : folder_object_metadata["LastModified"],
                                "ETag" : folder_object_metadata["ETag"],
                                "IsFile" : False,
                            }
                        case HCPHandler.ListObjectsOutputMode.SIMPLE:
                            yield {
                                "Key" : folder_object["Prefix"],
                                "LastModified" : folder_object_metadata["LastModified"],
                                "IsFile" : False,
                            }
                        case HCPHandler.ListObjectsOutputMode.NAME_ONLY:
                            yield {"Key" : folder_object["Prefix"]}   
            
            # Handle file objects
            for file_object in page.get("Contents", []):
                file_object : dict
                if file_object["Key"] != path_key:
                    file_object["IsFile"] = True
                    match output_mode:
                        case HCPHandler.ListObjectsOutputMode.EXTENDED:
                            yield file_object
                        case HCPHandler.ListObjectsOutputMode.SIMPLE:
                            yield {
                                "Key" : file_object["Key"],
                                "LastModified" : file_object["LastModified"],
                                "Size" : file_object["Size"],
                                "IsFile" : file_object["IsFile"]
                            }
                        case HCPHandler.ListObjectsOutputMode.NAME_ONLY:
                            yield {"Key" : file_object["Key"]}
                    
    @check_mounted
    def get_object(self, key : str) -> dict:
        """
        Retrieve object metadata

        :param key: The object name
        :type key: str

        :return: A dictionary containing the object metadata
        :rtype: dict
        """
        response = dict(self.s3_client.get_object(
            Bucket = self.bucket_name,
            Key = key
        ))
        return response

    @check_mounted
    def object_exists(self, key : str) -> bool:
        """
        Check if a given object is in the mounted bucket

        :param key: The object name
        :type key: str

        :return: True if the object exist, otherwise False
        :rtype: bool
        """
        try:
            response = self.get_object(key)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return True
            else: # pragma: no cover
                return False
        except: # pragma: no cover
            return False

    @check_mounted
    def download_file(self, key : str, local_file_path : str, show_progress_bar : bool = True) -> None:
        """
        Download one object file from the mounted bucket

        :param key: Name of the object
        :type key: str

        :param local_file_path: Path to a file on your local system where the contents of the object file can be put
        :type local_file_path: str

        :param show_progress_bar: Boolean choice of displaying a progress bar. Defaults to True
        :type show_progress_bar: bool, optional

        :raises ObjectDoesNotExist: If the object does not exist in the bucket
        """
        try:
            self.get_object(key)
        except:
            raise ObjectDoesNotExist("Could not find object", "\"" + key + "\"", "in bucket", "\"" + str(self.bucket_name) + "\"")
        try:
            if show_progress_bar:
                file_size : int = self.s3_client.head_object(Bucket = self.bucket_name, Key = key)["ContentLength"]
                with tqdm(
                    total = file_size, 
                    unit = "B", 
                    unit_scale = True, 
                    desc = key
                ) as pbar:
                    self.s3_client.download_file(
                        Bucket = self.bucket_name, 
                        Key = key, 
                        Filename = local_file_path, 
                        Config = self.transfer_config,
                        Callback = lambda bytes_transferred : pbar.update(bytes_transferred)
                    )
            else:
                self.s3_client.download_file(
                    Bucket = self.bucket_name, 
                    Key = key, 
                    Filename = local_file_path, 
                    Config = self.transfer_config,
                )
        except ClientError as e0: 
            raise e0
        except Exception as e: # pragma: no cover
            raise Exception(e)

    @check_mounted
    def download_folder(
            self, 
            folder_key : str, 
            local_folder_path : str, 
            use_download_limit : bool = False, 
            download_limit_in_bytes : Byte = TiB(1).to_Byte(), 
            show_progress_bar : bool = True
        ) -> None:  
        """
        Download multiple objects from a folder in the mounted bucket

        :param folder_key: Name of the folder
        :type folder_key: str

        :param local_folder_path: Path to a folder on your local system where the contents of the objects can be put
        :type local_folder_path: str

        :param use_download_limit: Boolean choice for using a download limit. Defaults to False
        :type use_download_limit: bool, optional

        :param download_limit_in_bytes: The optional download limit in Byte (from the package `bitmath`). Defaults to 1 TB (`TiB(1).to_Byte()`)
        :type download_limit_in_bytes: Byte, optional

        :param show_progress_bar: Boolean choice of displaying a progress bar. Defaults to True
        :type show_progress_bar: bool, optional
        
        :raises ObjectDoesNotExist: If the object does not exist in the bucket
        
        :raises DownloadLimitReached: If download limit was reached while downloading files
        
        :raises NotADirectory: If local_folder_path is not a directory
        """
        try:
            self.get_object(folder_key)
        except:
            raise ObjectDoesNotExist("Could not find object", "\"" + folder_key + "\"", "in bucket", "\"" + str(self.bucket_name) + "\"")
        if Path(local_folder_path).is_dir():
            current_download_size_in_bytes = Byte(0) # For tracking download limit
            (Path(local_folder_path) / Path(folder_key)).mkdir(parents = True) # Create "base folder"
            for object in self.list_objects(folder_key): # Build the tree with directories or add files:
                p = Path(local_folder_path) / Path(object["Key"])
                if not object["IsFile"]: # If the object is a "folder"
                    p.mkdir(parents = True)
                    self.download_folder(
                        folder_key = str(object["Key"]), 
                        local_folder_path = local_folder_path,
                        use_download_limit = use_download_limit, 
                        show_progress_bar = show_progress_bar,
                        download_limit_in_bytes = download_limit_in_bytes - current_download_size_in_bytes
                    )
                else: # If the object is a file
                    current_download_size_in_bytes += Byte(object["Size"])
                    if current_download_size_in_bytes >= download_limit_in_bytes and use_download_limit:
                        raise DownloadLimitReached("The download limit was reached when downloading files")
                    self.download_file(object["Key"], p.as_posix(), show_progress_bar = show_progress_bar)
        else:
            raise NotADirectory(local_folder_path + " is not a directory")
    
    class UploadMode(Enum):
        STANDARD = "standard"
        SIMPLE = "simple"
        EQUAL_PARTS = "equal_parts"

    @check_mounted
    def upload_file(self, local_file_path : str, key : str = "", show_progress_bar : bool = True, upload_mode : UploadMode = UploadMode.STANDARD, equal_parts : int = 5) -> None:
        """
        Upload one file to the mounted bucket

        :param local_file_path: Path to the file to be uploaded
        :type local_file_path: str

        :param key: An optional new name for the file object on the bucket. Defaults to the same name as the file
        :type key: str, optional

        :param show_progress_bar: Boolean choice of displaying a progress bar. Defaults to True
        :type show_progress_bar: bool, optional

        :param upload_mode: 
            The upload mode of the transfer is any of the following:\n
                HCPHandler.UploadMode.STANDARD,\n
                HCPHandler.UploadMode.SIMPLE,\n
                HCPHandler.UploadMode.EQUAL_PARTS\n
            Default is STANDARD
        :type upload_mode: UploadMode, optional

        :param equal_parts: The number of equal parts that each file should be divided into when using the HCPHandler.UploadMode.EQUAL_PARTS mode. Default is 5
        :type equal_parts: int, optional

        :raises RuntimeError: If the \"\\\" is used in the file path 
        
        :raises ObjectAlreadyExist: If the object already exist on the mounted bucket
        """
        raise_path_error(local_file_path)

        if not key:
            file_name = Path(local_file_path).name
            key = file_name

        if "\\" in local_file_path:
            raise RuntimeError("The \"\\\" character is not allowed in the file path")

        if self.object_exists(key):
            raise ObjectAlreadyExist("The object \"" + key + "\" already exist in the mounted bucket")
        else:
            file_size : int = stat(local_file_path).st_size

            match upload_mode:
                case HCPHandler.UploadMode.STANDARD:
                    config = self.transfer_config
                case HCPHandler.UploadMode.SIMPLE:
                    config = TransferConfig(multipart_chunksize = file_size)
                case HCPHandler.UploadMode.EQUAL_PARTS:
                    config = TransferConfig(multipart_chunksize = round(file_size / equal_parts))

            if show_progress_bar:
                with tqdm(
                    total = file_size, 
                    unit = "B", 
                    unit_scale = True, 
                    desc = local_file_path
                ) as pbar:
                    self.s3_client.upload_file(
                        Filename = local_file_path, 
                        Bucket = self.bucket_name, 
                        Key = key,
                        Config = config,
                        Callback = lambda bytes_transferred : pbar.update(bytes_transferred)
                    )
            else:
                self.s3_client.upload_file(
                    Filename = local_file_path, 
                    Bucket = self.bucket_name, 
                    Key = key,
                    Config = config,
                )

    @check_mounted
    def upload_folder(self, local_folder_path : str, key : str = "", show_progress_bar : bool = True, upload_mode : UploadMode = UploadMode.STANDARD, equal_parts : int = 5) -> None:
        """
        Upload the contents of a folder to the mounted bucket

        :param local_folder_path: Path to the folder to be uploaded
        :type local_folder_path: str

        :param key: An optional new name for the folder path on the bucket. Defaults to the same name as the local folder path
        :type key: str, optional

        :param show_progress_bar: Boolean choice of displaying a progress bar. Defaults to True
        :type show_progress_bar: bool, optional

        :param upload_mode: 
            The upload mode of the transfer is any of the following:
                HCPHandler.UploadMode.STANDARD,
                HCPHandler.UploadMode.SIMPLE,
                HCPHandler.UploadMode.EQUAL_PARTS\n
        :type upload_mode: UploadMode, optional

        :param equal_parts: The number of equal parts that each file should be divided into when using the HCPHandler.UploadMode.EQUAL_PARTS mode. Default is 5
        :type equal_parts: int, optional
        """
        raise_path_error(local_folder_path)

        if not key:
            key = local_folder_path
        filenames = listdir(local_folder_path)

        for filename in filenames:
            self.upload_file(
                local_folder_path + filename, 
                key + filename, 
                show_progress_bar = show_progress_bar, 
                upload_mode = upload_mode,
                equal_parts = equal_parts
            )

    @check_mounted
    def delete_objects(self, keys : list[str]) -> str:
        """
        Delete a list of objects on the mounted bucket 

        :param keys: List of object names to be deleted
        :type keys: list[str]

        :return: The result of the deletion 
        :rtype: str 
        """
        object_list = []
        does_not_exist = []
        for key in keys:
            if self.object_exists(key):
                object_list.append({"Key" : key})
            else:
                does_not_exist.append(key)

        result = ""
        if object_list:
            deletion_dict = {"Objects": object_list}
            response : dict = self.s3_client.delete_objects(
                Bucket = self.bucket_name,
                Delete = deletion_dict
            )
            
            deleted_files = list(d["Key"] for d in response["Deleted"])
            result += "The following was successfully deleted: \n" + "\n".join(deleted_files)
        
        if does_not_exist:
            result += "The following could not be deleted because they didn't exist: \n" + "\n".join(does_not_exist)
        
        return result
    
    @check_mounted
    def delete_object(self, key : str) -> str:
        """
        Delete a single object in the mounted bucket

        :param key: The object to be deleted
        :type key: str

        :return: The result of the deletion 
        :rtype: str 
        """
        return self.delete_objects([key])

    @check_mounted
    def delete_folder(self, key : str) -> str:
        """
        Delete a folder of objects in the mounted bucket. If there are subfolders, a RuntimeError is raised

        :param key: The folder of objects to be deleted
        :type key: str

        :raises RuntimeError: If there are subfolders, a RuntimeError is raised

        :return: The result of the deletion 
        :rtype: str
        """
        if key[-1] != "/":
            key += "/"

        objects : list[str] = list(
            obj["Key"] for obj in 
            self.list_objects(
                key, 
                output_mode = HCPHandler.ListObjectsOutputMode.NAME_ONLY
            )
        )
        objects.append(key) # Include the object "folder" path to be deleted

        if not objects:
            raise RuntimeError("\"" + key + "\"" + " is not a valid path") #TODO: change this error

        for object_path in objects:
            if (object_path[-1] == "/") and (not object_path == key): # `objects` might contain key, in which case everything is fine
                raise RuntimeError("There are subfolders in this folder. Please remove these first, before deleting this one")
        
        return self.delete_objects(objects)

    def delete_bucket(self, bucket : str) -> str:
        """
        Delete a specified bucket

        :param bucket: The bucket to be deleted
        :type bucket: str
        :return: The result of the deletion 
        :rtype: str 
        """
        self.s3_client.delete_bucket(
            Bucket = bucket
        )
        # If the deletion was not successful, `self.s3_client.delete_bucket` would have thrown an error 
        return bucket + " was successfully deleted"

    @check_mounted
    def search_in_bucket(
        self, 
        search_string : str, 
        case_sensitive : bool = False
    ) -> Generator:
        """
        Simple search method using exact substrings in order to find certain 
        objects. Case insensitive by default. Does not utilise the HCI

        :param search_string: Substring to be used in the search
        :type search_string: str

        :param case_sensitive: Case sensitivity. Defaults to False
        :type case_sensitive: bool, optional

        :return: A generator of objects based on the search string
        :rtype: Generator
        """
        return self.fuzzy_search_in_bucket(search_string, case_sensitive, 100)
        
    @check_mounted
    def fuzzy_search_in_bucket(
        self, 
        search_string : str, 
        case_sensitive : bool = False, 
        threshold : int = 80
    ) -> Generator:
        """
        Fuzzy search implementation based on the `RapidFuzz` library.

        :param search_string: Substring to be used in the search
        :type search_string: str

        :param name_only: If True, yield only a the object names. If False, yield the full metadata about each object. Defaults to False.
        :type name_only: bool, optional

        :param case_sensitive: Case sensitivity. Defaults to False
        :type case_sensitive: bool, optional

        :param threshold: The fuzzy search similarity score. Defaults to 80
        :type threshold: int, optional
        
        :return: A generator of objects based on the search string
        :rtype: Generator
        """
        
        if case_sensitive:
            processor = None
        else:
            processor = utils.default_process 

        full_list = peekable(self.list_objects(list_all_bucket_objects = True))

        full_list_names_only = peekable(
            obj["Key"] for obj in 
            self.list_objects(
                output_mode = HCPHandler.ListObjectsOutputMode.NAME_ONLY, 
                list_all_bucket_objects = True
            )
        )

        for _, score, index in process.extract_iter(
                search_string, 
                full_list_names_only,
                scorer = fuzz.partial_ratio,
                processor = processor
            ):
            if score >= threshold:
                yield full_list[index]

    @check_mounted
    def get_object_acl(self, key : str) -> dict:
        """
        Get the object Access Control List (ACL)

        :param key: The name of the object
        :type key: str

        :return: Return the ACL in the shape of a dictionary
        :rtype: dict
        """
        response : dict = self.s3_client.get_object_acl(
            Bucket = self.bucket_name,
            Key = key
        )
        return response

    @check_mounted
    def get_bucket_acl(self) -> dict:
        """
        Get the bucket Access Control List (ACL)

        :return: Return the ACL in the shape of a dictionary
        :rtype: dict
        """
        response : dict = self.s3_client.get_bucket_acl(
            Bucket = self.bucket_name
        )
        return response

    @check_mounted
    def modify_single_object_acl(self, key : str, user_ID : str, permission : str) -> None:
        """
        Modify permissions for a user in the Access Control List (ACL) for one object

        :param key: The name of the object
        :type key: str

        :param user_ID: The user name. Can either be the DisplayName or user_ID
        :type user_ID: str

        :param permission: 
            What permission to be set. Valid options are:
                * FULL_CONTROL 
                * WRITE 
                * WRITE_ACP 
                * READ 
                * READ_ACP\n
        :type permission: str
        """
        self.s3_client.put_object_acl(
            Bucket = self.bucket_name,
            Key = key,
            AccessControlPolicy = create_access_control_policy({user_ID : permission})
        )

    @check_mounted
    def modify_single_bucket_acl(self, user_ID : str, permission : str) -> None:
        """
        Modify permissions for a user in the Access Control List (ACL) for the mounted bucket

        :param user_ID: The user name. Can either be the DisplayName or user_ID
        :type user_ID: str
        
        :param permission: 
            What permission to be set. Valid options are: 
                * FULL_CONTROL 
                * WRITE 
                * WRITE_ACP 
                * READ 
                * READ_ACP\n
        :type permission: str
        """
        self.s3_client.put_bucket_acl(
            Bucket = self.bucket_name,
            AccessControlPolicy = create_access_control_policy({user_ID : permission})
        )

    @check_mounted
    def modify_object_acl(self, key_user_ID_permissions : dict[str, dict[str, str]]) -> None:
        """
        Modifies  permissions to multiple objects, see below.

        In order to add permissions for multiple objects, we make use of a dictionary of a dictionary: :py:obj:`key_user_ID_permissions = {key : {user_ID : permission}}`. So for every object (key), we set the permissions for every user ID for that object. 

        :param key_user_ID_permissions: The dictionary containing object name and user_id-permission dictionary
        :type key_user_ID_permissions: dict[str, dict[str, str]]
        """
        for key, user_ID_permissions in key_user_ID_permissions.items():
            self.s3_client.put_object_acl(
                Bucket = self.bucket_name,
                Key = key,
                AccessControlPolicy = create_access_control_policy(user_ID_permissions)
            )

    @check_mounted
    def modify_bucket_acl(self, user_ID_permissions : dict[str, str]) -> None:
        """
        Modify permissions for multiple users for the mounted bucket

        :param user_ID_permissions: The dictionary containing the user name and the corresponding permission to be set to that user
        :type user_ID_permissions: dict[str, str]
        """
        self.s3_client.put_bucket_acl(
            Bucket = self.bucket_name,
            AccessControlPolicy = create_access_control_policy(user_ID_permissions)
        )
