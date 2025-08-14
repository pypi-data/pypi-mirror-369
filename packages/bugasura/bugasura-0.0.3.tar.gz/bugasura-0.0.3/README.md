# Bugasura CLI .xml Uploader

A Bugasura CLI tool to upload a single `.xml` file or all `.xml` files in a folder to upload the Test run results.

---

## 📦 Installation

Install locally from source:

```
bash
pip install bugasura
```

## 🚀 Usage

Upload a single .xml file:

bugasura ACTION ./path/to/file.xml --api_key [Your API Key] --team_id [Bugasura Team Id] --project_id [Bugasura Project Id] --testrun_id [Bugasura Testrun Id (optional)] --server [Server Name (optional)]

Upload all .xml files from a folder:

bugasura ACTION ./path/to/folder --api_key [Your API Key] --team_id [Bugasura Team Id] --project_id [Bugasura Project Id] --testrun_id [Bugasura Testrun Id (optional)] --server [Server Name (optional)]


## ⚠️ Rules

	Only .xml files are allowed.

	Invalid paths or non-XML files will raise errors.

	For folders, only .xml files will be uploaded.


## 📂 Project Structure


	bugasura/
	├── bugasura/
	│	├── uploader.py
	│	├── cli.py
	│	└── __init__.py
	│	└── config.py
	├── setup.py
	├── bugasura.toml
	└── README.md


## ✅ License