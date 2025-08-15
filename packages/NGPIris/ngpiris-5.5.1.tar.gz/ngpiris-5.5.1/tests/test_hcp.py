
from pathlib import Path
from filecmp import cmp
from typing import Any, Callable
from conftest import CustomConfig
from NGPIris.hcp import HCPHandler
from icecream import ic

# --------------------------- Helper fucntions ---------------------------------

def _without_mounting(hcp_h : HCPHandler, hcp_h_method : Callable[..., Any]) -> None:
    hcp_h.bucket_name = None
    try:
        hcp_h_method(hcp_h)
    except:
        assert True
    else: # pragma: no cover
        assert False

# --------------------------- Test suite ---------------------------------------

def test_list_buckets(custom_config : CustomConfig) -> None:
    assert custom_config.hcp_h.list_buckets() 

def test_mount_bucket(custom_config : CustomConfig) -> None:
    custom_config.hcp_h.mount_bucket(custom_config.test_bucket) 

def test_mount_nonexisting_bucket(custom_config : CustomConfig) -> None:
    try:
        custom_config.hcp_h.mount_bucket("aBucketThatDoesNotExist") 
    except:
        assert True
    else: # pragma: no cover
        assert False

def test_test_connection(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    custom_config.hcp_h.test_connection() 

def test_test_connection_with_bucket_name(custom_config : CustomConfig) -> None:
    custom_config.hcp_h.test_connection(bucket_name = custom_config.test_bucket) 

def test_test_connection_without_mounting_bucket(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.test_connection)

def test_list_objects(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    assert type(list(custom_config.hcp_h.list_objects())) == list 

def test_list_objects_without_mounting(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.list_objects)

def test_upload_file(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    
    # With progress bar
    custom_config.hcp_h.upload_file(
        custom_config.test_file_path, 
        custom_config.test_file_path
    )
    
    # Without progress bar
    custom_config.hcp_h.upload_file(
        custom_config.test_file_path, 
        custom_config.test_file_path + "_no_progress_bar", 
        show_progress_bar = False
    )

    # Test every upload mode
    for mode in HCPHandler.UploadMode:
        ic(mode, custom_config.test_file_path + "_" + str(mode).replace(".", "_"))
        custom_config.hcp_h.upload_file(
            custom_config.test_file_path, 
            custom_config.test_file_path + "_" + str(mode).replace(".", "_"),
            upload_mode = mode
        )

def test_upload_file_without_mounting(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.upload_file)

def test_upload_file_in_sub_directory(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    custom_config.hcp_h.upload_file(custom_config.test_file_path, "a_sub_directory/a_file") 

def test_upload_nonexistent_file(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    try: 
        custom_config.hcp_h.upload_file("tests/data/aTestFileThatDoesNotExist") 
    except:
        assert True
    else: # pragma: no cover
        assert False

def test_upload_folder(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    custom_config.hcp_h.upload_folder("tests/data/a folder of data/", "a folder of data/") 

def test_upload_folder_without_mounting(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.upload_folder)

def test_upload_nonexisting_folder(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    try: 
        custom_config.hcp_h.upload_folder("tests/data/aFolderOfFilesThatDoesNotExist") 
    except:
        assert True
    else: # pragma: no cover
        assert False

def test_get_file(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    assert custom_config.hcp_h.object_exists("a_sub_directory/a_file") 
    assert custom_config.hcp_h.get_object("a_sub_directory/a_file") 

def test_get_folder_without_mounting(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.object_exists)
    _without_mounting(_hcp_h, HCPHandler.get_object)

def test_get_file_in_sub_directory(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    assert custom_config.hcp_h.object_exists(custom_config.test_file_path) 
    assert custom_config.hcp_h.get_object(custom_config.test_file_path) 

def test_download_file(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    Path(custom_config.result_path).mkdir()
    
    test_folder_path = str(custom_config.test_file_path).rsplit("/", maxsplit = 1)[0] + "/"
    Path(custom_config.result_path + test_folder_path).mkdir(parents = True, exist_ok = True)

    # With progress bar
    custom_config.hcp_h.download_file(custom_config.test_file_path, custom_config.result_path + custom_config.test_file_path)
    assert cmp(custom_config.result_path + custom_config.test_file_path, custom_config.test_file_path) 

    # Without progress bar
    custom_config.hcp_h.download_file(
        custom_config.test_file_path + "_no_progress_bar", 
        custom_config.result_path + custom_config.test_file_path + "_no_progress_bar",
        show_progress_bar = False
    )
    assert cmp(custom_config.result_path + custom_config.test_file_path, custom_config.test_file_path) 

def test_download_file_without_mounting(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.download_file)

def test_download_nonexistent_file(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    try:
        custom_config.hcp_h.download_file("aFileThatDoesNotExist", custom_config.result_path + "aFileThatDoesNotExist") 
    except:
        assert True
    else: # pragma: no cover
        assert False

def test_download_folder(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    custom_config.hcp_h.download_folder("a folder of data/", custom_config.result_path) 

def test_search_in_bucket(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    test_file = Path(custom_config.test_file_path).name 
    custom_config.hcp_h.search_in_bucket(test_file) 

def test_search_in_bucket_without_mounting(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.search_in_bucket)

def test_fuzzy_search_in_bucket(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    test_file = Path(custom_config.test_file_path).name 
    custom_config.hcp_h.fuzzy_search_in_bucket(test_file) 

def test_fuzzy_search_in_bucket_without_mounting(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.fuzzy_search_in_bucket)

def test_get_object_acl(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    custom_config.hcp_h.get_object_acl(custom_config.test_file_path) 

def test_get_object_acl_without_mounting(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.get_object_acl)

def test_get_bucket_acl(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    custom_config.hcp_h.get_bucket_acl() 

def test_get_bucket_acl_without_mounting(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.get_bucket_acl)

# ------------------ Possibly future ACL tests ---------------------------------

#def test_modify_single_object_acl(custom_config : CustomConfig) -> None:
#    test_mount_bucket(custom_config)
#    custom_config.hcp_h.modify_single_object_acl()
#
#def test_modify_single_bucket_acl(custom_config : CustomConfig) -> None:
#    test_mount_bucket(custom_config)
#    custom_config.hcp_h.modify_single_bucket_acl()
#
#def test_modify_object_acl(custom_config : CustomConfig) -> None:
#    test_mount_bucket(custom_config)
#    custom_config.hcp_h.modify_object_acl()
#
#def test_modify_bucket_acl(custom_config : CustomConfig) -> None:
#    test_mount_bucket(custom_config)
#    custom_config.hcp_h.modify_bucket_acl()

# ------------------------------------------------------------------------------

def test_delete_file(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    custom_config.hcp_h.delete_object(custom_config.test_file_path) 
    custom_config.hcp_h.delete_object(custom_config.test_file_path + "_no_progress_bar")
    for mode in HCPHandler.UploadMode:
        custom_config.hcp_h.delete_object(custom_config.test_file_path + "_" + str(mode).replace(".", "_"))
    custom_config.hcp_h.delete_object("a_sub_directory/a_file") 
    custom_config.hcp_h.delete_object("a_sub_directory") 

def test_delete_file_without_mounting(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.delete_object)

def test_delete_folder_with_sub_directory(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    custom_config.hcp_h.upload_file(custom_config.test_file_path, "a folder of data/a sub dir/a file") 
    try:
        custom_config.hcp_h.delete_folder("a folder of data/") 
    except: 
        assert True
    else: # pragma: no cover 
        assert False
    custom_config.hcp_h.delete_folder("a folder of data/a sub dir/") 

def test_delete_folder(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    custom_config.hcp_h.delete_folder("a folder of data/") 

def test_delete_folder_without_mounting(custom_config : CustomConfig) -> None:
    _hcp_h = custom_config.hcp_h 
    _without_mounting(_hcp_h, HCPHandler.delete_folder)

def test_delete_nonexistent_files(custom_config : CustomConfig) -> None:
    test_mount_bucket(custom_config)
    custom_config.hcp_h.delete_objects(["some", "files", "that", "does", "not", "exist"]) 
