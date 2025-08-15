# streamlit-chemui

Streamlit component that allows you to do X

## Installation instructions

```sh
pip install streamlit-chemui
```

## Usage instructions

```python
import json
import streamlit as st

from chemui import ChemList, Smiles

DemoCSV = {
    "visual_data": [
        {
            "name": "csv的Demo名称",
            "description": "csv的Demo内容描述",
            "files": [
                {
                    "type": "CSV",
                    "name": "csv的展示名称",
                    "description": "csv的展示描述",
                    "path": "http://localhost:5500/CDK9_actives.csv",
                    "download_url": "http://localhost:5500/CDK9_actives.csv",
                    "format": "csv"
                }
            ],
            "download_url": "http://localhost:5500/CDK9_actives.csv"
        }
    ]
};

DemoCSV1 = json.dumps(DemoCSV)
ChemList(DemoCSV)
```

```python
import json
import streamlit as st

from chemui import ChemList, Smiles

Smiles("CC(=O)OC1=CC=CC=C1C(=O)O")
```