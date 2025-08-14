# Contributing

Thank you for your interest in contributing! 🤗

<br>

## 🐞 Workflow for bug reports, feature requests and documentation improvements

Before opening an issue, please search [existing issues](https://github.com/lintquarto/lintquarto/issues/) to avoid duplicates. If there is not an existing issue, please open open and provide as much detail as possible.

* **For feature requests or documentation improvements**, please describe your suggestion clearly.
* **For bugs**, include:
    * Steps to reproduce.
    * Expected and actual behaviour.
    * Environment details (operating system, python version, dependencies).
    * Relevant files (e.g. problematic `.qmd` files).

### Handling bug reports (for maintainers):

* Confirm reproducibility by following the reported steps.
* Label the issue appropriately (e.g. `bug`).
* Request additional information if necessary.
* Link related issues or pull requests.
* One resolved, close the issue with a brief summary of the fix.

<br>

## 🚀 Workflow for code contributions (bug fixes, enhancements)

1. Fork the repository and clone your fork.

2. Create a new branch for your feature or fix:

```{.bash}
git checkout -b my-feature
```

3. Make your changes and commit them with clear, descriptive messages using the [conventional commits standard](https://www.conventionalcommits.org/en/v1.0.0/).

4. Push your branch to your fork:

```{.bash}
git push origin my-feature
```

5. Open a pull request against the main branch. Describe your changes and reference any related issues.

<br>

## 🛠️ Development and testing

### Dependencies

If you want to contribute to `lintquarto` or run its tests, you'll need some additional tools:

| Tool | Purpose |
| - | - |
| **check-dependencies** | Test for undeclared dependencies |
| **flit** | Packaging and publishing |
| **genbadge** | Create coverage badge (README) |
| **jupyter** | Run python code in docs |
| **pytest** | Run tests |
| **pytest-cov** | Calculate coverage |
| **twine** | Upload to PyPI
| **quartodoc** | Generate API docs |
| `-e .[all]` | Editable install + all linters |

These are listed in `requirements-dev.txt` for convenience. To set up your development environment, run:

```{.bash}
pip install -r requirements-dev.txt
```

For testing only (used by GitHub actions):

```{.bash}
pip install -r requirements-test.txt
```

Quarto (used for the docs) is a standalone tool - install it from https://quarto.org/docs/get-started/.

<br>

### Dependency versions

Contributors are encouraged to install and use the **latest versions** of development tools. This helps keep the project compatible with current tooling and catches issues early.

If you need a fully reproducible and stable setup, use the provided Conda environment file. This file pins all development tool versions, including Python:

```{.bash}
conda env create -f requirements-stable.yml
```

To update the stable environment, run `conda update --all` and test thoroughly (running tests, building documentation), and then update `requirements-stable.yml` with any changes.

<br>

### Tests

Run all tests (with coverage):

```{.bash}
pytest --cov
```

<br>

### Linting

Make scripts executable (first time only):

```{.bash}
chmod +x lint_package.sh
chmod +x lint_docs.sh
```

Lint the package:

```{.bash}
lint_package.sh
```

Lint the documentation:

```{.bash}
lint_docs.sh
```

<br>

### Documentation

Build and preview the documentation locally:

```{.bash}
make -C docs
```

<br>

## 📦 Updating the package

If you are a maintainer and need to publish a new release:

1. Update the `CHANGELOG.md`.

2. Update the version number in `__init__.py`, `CITATION.cff` and `README.md` citation, and update the date in `CITATION.cff`.

3. Create a release on GitHub, which will automatically archive to Zenodo.

4. Build and publish using flit or twine.

To upload to PyPI using `flit`:

```{.bash}
flit publish
```

To upload to PyPI using `twine`: remove any existing builds, then build the package locally and push with twine, entering the API token when prompted:

```{.bash}
rm -rf dist/
flit build
twine upload --repository pypi dist/*
```

For test runs, you can use the same method with test PyPI:

```{.bash}
rm -rf dist/
flit build
twine upload --repository testpypi dist/*
```

<br>

## 🤝 Code of conduct

Please be respectful and considerate. See the [code of conduct](https://github.com/lintquarto/lintquarto/blob/main/CODE_OF_CONDUCT.md) for details.