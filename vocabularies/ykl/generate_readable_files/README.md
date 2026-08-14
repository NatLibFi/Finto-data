
# Kuinka generoin YKL:n luokkahierarkian tiedostoihin (txt, md, csv, docx)

```cd /Finto-data/vocabularies/ykl/generate_readable_files/```

```. /[python-virtuaaliympäristösi juuri]/bin/activate```

```python3 -m pip install rdflib python-docx```

```python3 -m pip install openpyxl```

```cp -p ../ykl-vb-skos.ttl .```

```python3 ykl_export.py ykl-vb-skos.ttl```

```ls -la ykl_export```
