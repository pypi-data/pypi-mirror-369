from .ATmulti_file_handler import File,TextFile,ByteFile,JsonFile,XmlFile,CsvFile,DillFile, YamlFile


def open_file( file_name: str, file_path: str = ".", create_if_missing: bool = True)-> TextFile | JsonFile | YamlFile | CsvFile | XmlFile | DillFile | ByteFile:
    """
        Basic function for opening common files will return the appropriate file Class

        Args:
            file_name (str): The name of the file (including extension).
            file_path (str, optional): Directory path to store the file. Defaults to the current directory.
            create_if_missing (bool, optional): Whether to create the file if it does not exist. Defaults to True.

        Attributes:
            file_name (str): File name.
            file_path (str): File path.
        """
    if file_name.endswith(".txt"): return TextFile(file_name,file_path,create_if_missing)
    elif file_name.endswith(".json"): return JsonFile(file_name,file_path,create_if_missing)
    elif file_name.endswith((".yml",".yaml")): return YamlFile(file_name,file_path,create_if_missing)
    elif file_name.endswith(".csv"): return CsvFile(file_name,file_path,create_if_missing)
    elif file_name.endswith(".xml"): return XmlFile(file_name,file_path,create_if_missing)
    elif file_name.endswith((".pkl",".dill")): return DillFile(file_name,file_path,create_if_missing)
    elif file_name.endswith((".bin",".dat")): return ByteFile(file_name,file_path,create_if_missing)
    else: raise ValueError(f"this function does not support {file_name} try using manually" )

