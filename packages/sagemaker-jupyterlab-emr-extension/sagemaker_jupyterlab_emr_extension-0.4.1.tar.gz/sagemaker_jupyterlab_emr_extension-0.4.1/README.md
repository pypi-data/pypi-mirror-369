# sagemaker_jupyterlab_emr_extension

This package includes the extension built by SageMaker team that includes provides EMR connectivity feature for JupyterLab. 

### Installing the extension
To install the extension within local Jupyter environment, a Docker image/container or in SageMaker Studio, run:
```
pip install sagemaker_jupyterlab_emr_extension-<version>-py3-none-any.whl`
```

### Uninstalling the extension
To uninstall this extension, run:
```
pip uninstall sagemaker_jupyterlab_emr_extension`
```

### Watch Mode
To see local dev changes in real time, run 
```
npm run watch
```

Then in a new terminal, run
```
jupyter-lab
```
You should see the local changes in the new JupyterLab browser tab

### Troubleshooting
Make sure to have node >=16 and Python >=3.9 installed in your dev desktop

If you are seeing the frontend extension, but it is not working, check that the server extension is enabled:

```
jupyter serverextension list
```

If the server extension is installed and enabled, but you are not seeing the frontend extension, check the frontend extension is installed:
```
jupyter labextension list
```

If the frontend extension is installed and enabled, open Browser console and see if there are any JavaScript error that is related to the extension in Browser console.

## See DEVELOPING.md for more instructions on dev setup and contributing guidelines
