from __future__ import annotations
from typing import Protocol, Any, runtime_checkable
from pathlib import Path
import json
import dill
import csv
import yaml
import xml.etree.ElementTree as ET


@runtime_checkable
class File(Protocol):
    """
    Protocol that defines a file interface.

    Attributes:
        file_name (str): The name of the file (including extension).
        file_path (str): The directory where the file is located.
    """

    file_name: str
    file_path: str

    def read(self) -> Any:
        """
        Reads data from the file.

        Returns:
            Any: The file content, format depends on the file type.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        ...

    def write(self, data: Any) -> None:
        """
        Writes data to the file.

        Args:
            data (Any): The data to write.

        Raises:
            OSError: If the file cannot be written.
        """
        ...


class BaseFile:
    """
    Base class for common file operations and validations.

    Args:
        file_name (str): The name of the file (including extension).
        file_path (str, optional): Directory path to store the file. Defaults to the current directory.
        create_if_missing (bool, optional): Whether to create the file if it does not exist. Defaults to True.

    Attributes:
        file_name (str): File name.
        file_path (str): File path.
    """

    def __init__(self, file_name: str, file_path: str = ".", create_if_missing: bool = True) -> None:
        self.file_name = file_name
        self.file_path = file_path
        self._full_path = Path(file_path) / file_name
        self._full_path.parent.mkdir(parents=True, exist_ok=True)

        if not self._full_path.exists():
            if create_if_missing:
                self._create_empty_file()
        elif self._full_path.stat().st_size == 0 and create_if_missing:
            # Handle existing but empty files
            self._create_empty_file()

    def _create_empty_file(self) -> None:
        """
        Creates an empty file according to the file type.
        Can be overridden in subclasses.
        """
        self._full_path.touch()

    def _check_exists(self) -> None:
        """
        Ensures the file exists before attempting read or write.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not self._full_path.exists():
            raise FileNotFoundError(f"File not found: {self._full_path}")

    def path(self) -> Path:
        """
        Returns the full file path.

        Returns:
            Path: The full path to the file.
        """
        return self._full_path


class TextFile(BaseFile):
    """
    Text file handler.
    Supports read, write, and append operations.

    Args:
        file_name (str): The name of the text file.
        file_path (str, optional): The directory path. Defaults to current directory.
        create_if_missing (bool, optional): Whether to create the file if it does not exist. Defaults to True.
    """

    def __init__(self, file_name: str, file_path: str = ".", create_if_missing: bool = True) -> None:
        super().__init__(file_name)

    def read(self) -> str:
        self._check_exists()
        with self._full_path.open("r", encoding="utf-8") as f:
            return f.read()

    def write(self, data: str) -> None:
        with self._full_path.open("w", encoding="utf-8") as f:
            f.write(data)

    def append(self, data: str) -> None:
        with self._full_path.open("a", encoding="utf-8") as f:
            f.write(data)


class JsonFile(BaseFile):
    """
    JSON file handler.
    Supports read, write, and append operations.

    Args:
        file_name (str): The name of the JSON file.
        file_path (str, optional): The directory path. Defaults to current directory.
        create_if_missing (bool, optional): Whether to create the file if it does not exist. Defaults to True.
    """

    def __init__(self, file_name: str, file_path: str = ".", create_if_missing: bool = True) -> None:
        super().__init__(file_name)

    def _create_empty_file(self) -> None:
        self.write({})

    def read(self) -> Any:
        self._check_exists()

        if self._full_path.stat().st_size == 0:
            raise ValueError("JSON file exists but is empty.")

        with self._full_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def write(self, data: Any) -> None:
        with self._full_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def append(self, data: tuple[str, Any]) -> None:
        key, value = data
        content = self.read()

        if not isinstance(content, dict):
            raise ValueError("JSON file content is not a dictionary.")

        content[key] = value
        self.write(content)


class DillFile(BaseFile):
    """
    Dill file handler.
    Supports read and write using dill serialization.

    Args:
        file_name (str): The name of the dill file.
        file_path (str, optional): The directory path. Defaults to current directory.
        create_if_missing (bool, optional): Whether to create the file if it does not exist. Defaults to True.
    """

    def __init__(self, file_name: str, file_path: str = ".", create_if_missing: bool = True) -> None:
        super().__init__(file_name)

    def _create_empty_file(self) -> None:
        self.write(None)

    def read(self) -> Any:
        self._check_exists()

        if self._full_path.stat().st_size == 0:
            raise ValueError("Dill file exists but is empty.")

        with self._full_path.open("rb") as f:
            return dill.load(f)

    def write(self, data: Any) -> None:
        with self._full_path.open("wb") as f:
            dill.dump(data, f)


class ByteFile(BaseFile):
    """
    Binary file handler.
    Supports read and write in bytes mode.

    Args:
        file_name (str): The name of the binary file.
        file_path (str, optional): The directory path. Defaults to current directory.
        create_if_missing (bool, optional): Whether to create the file if it does not exist. Defaults to True.
    """

    def __init__(self, file_name: str, file_path: str = ".", create_if_missing: bool = True) -> None:
        super().__init__(file_name)

    def read(self) -> bytes:
        self._check_exists()
        with self._full_path.open("rb") as f:
            return f.read()

    def write(self, data: bytes) -> None:
        with self._full_path.open("wb") as f:
            f.write(data)


class YamlFile(BaseFile):
    """
    YAML file handler.
    Supports read and write operations.

    Args:
        file_name (str): The name of the YAML file.
        file_path (str, optional): The directory path. Defaults to current directory.
        create_if_missing (bool, optional): Whether to create the file if it does not exist. Defaults to True.
    """

    def __init__(self, file_name: str, file_path: str = ".", create_if_missing: bool = True) -> None:
        super().__init__(file_name)

    def _create_empty_file(self) -> None:
        self.write({})

    def read(self) -> Any:
        self._check_exists()
        if self._full_path.stat().st_size == 0:
            raise ValueError("YAML file exists but is empty.")
        with self._full_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def write(self, data: Any) -> None:
        with self._full_path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False)

    def append(self, data: dict) -> None:
        current = self.read()
        if not isinstance(current, dict):
            raise ValueError("YAML content must be a dictionary to append.")
        current.update(data)
        self.write(current)


class CsvFile(BaseFile):
    """
    CSV file handler.
    Supports read and write of list of dicts (rows).

    Args:
        file_name (str): The name of the CSV file.
        file_path (str, optional): The directory path. Defaults to current directory.
        create_if_missing (bool, optional): Whether to create the file if it does not exist. Defaults to True.
    """

    def __init__(self, file_name: str, file_path: str = ".", create_if_missing: bool = True) -> None:
        super().__init__(file_name)

    def _create_empty_file(self) -> None:
        self.write([])

    def read(self) -> list[dict[str, Any]]:
        self._check_exists()
        if self._full_path.stat().st_size == 0:
            return []
        with self._full_path.open("r", encoding="utf-8", newline='') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def write(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            self._full_path.write_text("")
            return

        with self._full_path.open("w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def append(self, row: dict[str, Any]) -> None:
        exists = self._full_path.exists() and self._full_path.stat().st_size > 0
        with self._full_path.open("a", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not exists:
                writer.writeheader()
            writer.writerow(row)


class XmlFile(BaseFile):
    """
    XML file handler.
    Supports reading and writing of XML trees.

    Args:
        file_name (str): The name of the XML file.
        file_path (str, optional): The directory path. Defaults to current directory.
        create_if_missing (bool, optional): Whether to create the file if it does not exist. Defaults to True.
    """

    def __init__(self, file_name: str, file_path: str = ".", create_if_missing: bool = True) -> None:
        super().__init__(file_name)

    def _create_empty_file(self) -> None:
        root = ET.Element("root")
        tree = ET.ElementTree(root)
        tree.write(self._full_path, encoding="utf-8", xml_declaration=True)

    def read(self) -> ET.Element:
        self._check_exists()
        if self._full_path.stat().st_size == 0:
            raise ValueError("XML file exists but is empty.")
        tree = ET.parse(self._full_path)
        return tree.getroot()

    def write(self, root: ET.Element) -> None:
        tree = ET.ElementTree(root)
        tree.write(self._full_path, encoding="utf-8", xml_declaration=True)

    def append(self, element: ET.Element) -> None:
        root = self.read()
        root.append(element)
        self.write(root)


# Example usage
if __name__ == "__main__":
    def read_file(file: File):
        """Example function to read from any File implementation."""
        print(file.read())


    def write_to_file(file: File, data: Any):
        """Example function to write to any File implementation."""
        file.write(data)


    my_file = TextFile("file.txt")
    write_to_file(my_file, "hi how are you")
    read_file(my_file)

    yaml_file = YamlFile("data.yaml")
    yaml_file.write({"name": "Alice", "age": 30})
    print(yaml_file.read())
    yaml_file.append({"country": "Israel"})

    csv_file = CsvFile("people.csv")
    csv_file.write([{"name": "Alice", "age": 30}])
    print(csv_file.read())
    csv_file.append({"name": "Bob", "age": 25})

    xml_file = XmlFile("data.xml")
    root = ET.Element("people")
    person = ET.Element("person")
    person.set("name", "Alice")
    root.append(person)
    xml_file.write(root)

    new_person = ET.Element("person")
    new_person.set("name", "Bob")
    xml_file.append(new_person)
