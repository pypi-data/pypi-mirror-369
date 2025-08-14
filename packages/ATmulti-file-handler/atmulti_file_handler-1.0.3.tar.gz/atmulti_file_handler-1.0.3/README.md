
````markdown
# ATmulti_file_handler

**ATmulti_file_handler** is a Python package for seamless reading and writing of multiple file formats with a unified, object-oriented API.  
It supports text, JSON, YAML, CSV, XML, pickle-like (Dill), and raw binary files — all under a common interface.

---

## ✅ Features

- Unified interface using a `File` protocol
- Automatic file creation (optional)
- Built-in support for:
  - Plain text (`.txt`)
  - JSON (`.json`)
  - YAML (`.yaml`, `.yml`)
  - CSV (`.csv`)
  - XML (`.xml`)
  - Serialized binary using `dill` (`.pkl`, `.dill`)
  - Raw binary (`.bin`, `.dat`, etc.)
- Easy extension for other formats
- Append support where applicable
- open_file function to auto create appropriate file Class

---

## 📦 Installation

Install via pip:

```bash
pip install ATmulti_file_handler
````

---

## 🧪 Supported File Types and Usage

### TextFile

```python
from ATmulti_file_handler import TextFile

txt = TextFile("example.txt")
txt.write("Hello world")
print(txt.read())
txt.append("\nThis is appended.")
```

---

### JsonFile

```python
from ATmulti_file_handler import JsonFile

js = JsonFile("data.json")
js.write({"name": "Alice"})
print(js.read())
js.append(("age", 30))  # appends key-value
```

---

### YamlFile

```python
from ATmulti_file_handler import YamlFile

yml = YamlFile("config.yaml")
yml.write({"env": "dev"})
print(yml.read())
yml.append({"version": "1.0.0"})
```

---

### CsvFile

```python
from ATmulti_file_handler import CsvFile

csvf = CsvFile("people.csv")
csvf.write([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
])
print(csvf.read())
csvf.append({"name": "Charlie", "age": 22})
```

---

### XmlFile

```python
from ATmulti_file_handler import XmlFile
import xml.etree.ElementTree as ET

xmlf = XmlFile("data.xml")
root = ET.Element("people")
person = ET.Element("person")
person.set("name", "Alice")
root.append(person)
xmlf.write(root)

# Append new element
new_person = ET.Element("person")
new_person.set("name", "Bob")
xmlf.append(new_person)

print(ET.tostring(xmlf.read()))
```

---

### DillFile

```python
from ATmulti_file_handler import DillFile

dillf = DillFile("model.dill")
dillf.write({"model": [1, 2, 3]})
print(dillf.read())
```

---

### ByteFile

```python
from ATmulti_file_handler import ByteFile

bf = ByteFile("raw.bin")
bf.write(b'\x00\x01\x02')
print(bf.read())
```

---

## 📁 Design Philosophy

All file types inherit from a shared base class `BaseFile`, which handles:

* Path creation and validation
* Auto-creation of empty files
* Unified error handling
* Standard interface: `read()` and `write()`
  Some classes also provide `append()` methods.

You can work with any file using the shared `File` protocol:

```python
from ATmulti_file_handler import File

def process_file(f: File):
    print("File contents:", f.read())
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 🔗 Project Links

* **PyPI**: [https://pypi.org/project/ATmulti\_file\_handler](https://pypi.org/project/ATmulti_file_handler) 
* **GitHub**: [https://github.com/avitwil/ATmulti\_file\_handler](https://github.com/avitwil/ATmulti_file_handler)

---

## 👤 Author

**Avi Twil**


---

## 🧩 Future Features (Ideas)

* Support for Excel (.xlsx) via `openpyxl`
* Automatic schema inference for CSV
* Logging and error handling improvements
* GUI/CLI integration

---


