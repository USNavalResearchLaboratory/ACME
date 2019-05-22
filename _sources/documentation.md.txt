# Documentation
This documentation was built with [Sphinx](http://www.sphinx-doc.org) 1.8.4 and [Recommonmark](http://recommonmark.readthedocs.org) 0.5, and uses the [Numpy docstring format](https://numpydoc.readthedocs.io/en/latest/format.html).


## How to build
Ensure all requirements are installed:
```
pip3 install --user -r requirements.txt
```
*Note: User may wish to use Python Virtual Environments or install globally instead of installing packages in their local user directory.  If so, ``--user`` may be omitted.*

Navigate to the `docs` folder:
```
cd docs
```

If necessary, edit the `Makefile`.
Set the `SPHINXBUILD` variable to the appropriate location of `sphinx-build` if not in the default location.

Query which `build` targets are available:
```
make
```

Select a `build` target to compile.  For example, to build `html` documentation:
```
make html
```

