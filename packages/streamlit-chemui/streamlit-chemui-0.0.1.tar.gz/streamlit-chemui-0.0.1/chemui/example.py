import json

import streamlit as st
from chemui import ChemList, Smiles

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/example.py`

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
# st.set_page_config(layout="wide")
# Demo转换为json格式
DemoCSV1 = json.dumps(DemoCSV)
print(DemoCSV1)
ChemList(DemoCSV)
Smiles("CC(=O)OC1=CC=CC=C1C(=O)O")
