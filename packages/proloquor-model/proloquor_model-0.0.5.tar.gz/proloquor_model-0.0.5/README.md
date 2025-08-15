# Proloquor Model

Useful python classes that model and examine proloquor.net surveys.  To download the package from [PyPi](https://pypi.org/project/proloquor-model/):

```bash
% pip install proloquor-model
```

## Development Setup

```powershell   
PS C:\proloquor-model>git clone git@gitlab.com:proloquor-public/proloquor-model.git
PS C:\proloquor-model> python -m venv .venv
PS C:\proloquor-model> .venv\Scripts\Activate.ps1
(.venv) PS C:\proloquor-model> python -m pip install pip --upgrade
(.venv) PS C:\proloquor-model> pip install pip-tools
(.venv) PS C:\proloquor-model> pip-compile --upgrade
(.venv) PS C:\proloquor-model> pip install -r requirements.txt
(.venv) PS C:\proloquor-model> pytest
```

Once you make any changes to the code, perform the following steps to upload the source to gitlab and the executable library to [pypi.org](https://packaging.python.org/en/latest/tutorials/packaging-projects/).  

```powershell
(.venv) PS C:\proloquor-model> git commit git@gitlab.com:proloquor-public/proloquor-model.git
```

Update the version in pyproject.toml:
```python
[project]
name = "proloquor-model"
version = "0.0.1"
authors = [
  { name="Proloquor.net Staff", email="staff@proloquor.net" },
]
```
Build the library and deploy it to pypi.org using twine.  You'll be prompted for your pypi.org [API key](https://pypi.org/help/#apitoken).  

```powershell
(.venv) PS C:\proloquor-model> pip install build
(.venv) PS C:\proloquor-model> python3 -m build
(.venv) PS C:\proloquor-model>pip install twine
(.venv) PS C:\proloquor-model>python3 -m twine upload dist/*
```
