build:
    python setup.py sdist

upload:
    python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*