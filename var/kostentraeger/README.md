# Kostenträgerdateien (operator cache)

Downloaded SLE files from [GKV Datenaustausch](https://www.gkv-datenaustausch.de/leistungserbringer/sonstige_leistungserbringer/kostentraegerdateien_sle/kostentraegerdateien.jsp).

`.ke*` files and `store.json` are gitignored. Refresh with:

```powershell
uv run python packages/ta5py/scripts/download_kostentraeger.py
```
