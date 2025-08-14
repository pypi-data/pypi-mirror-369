# edgar-sec

## A feature-rich python package for interacting with the US Securities and Exchange Commission API: EDGAR

<div align="center">
    <img src="https://github.com/nikhilxsunder/edgar-sec/blob/main/docs/source/_static/edgar-sec-logo.png" width="30%" alt="Edgar-SEC Logo">
</div>

<div align="center">
    <a href="https://github.com/nikhilxsunder/edgar-sec/actions/workflows/main.yml"><img src="https://github.com/nikhilxsunder/edgar-sec/actions/workflows/main.yml/badge.svg" alt="Build and test GitHub"></a>
    <a href="https://github.com/nikhilxsunder/edgar-sec/actions/workflows/analyze.yml"><img src="https://github.com/nikhilxsunder/edgar-sec/actions/workflows/analyze.yml/badge.svg" alt="Analyze Status"></a>
    <a href="https://github.com/nikhilxsunder/edgar-sec/actions/workflows/test.yml"><img src="https://github.com/nikhilxsunder/edgar-sec/actions/workflows/test.yml/badge.svg" alt="Test Status"></a>
    <a href="https://github.com/nikhilxsunder/edgar-sec/actions/workflows/codeql.yml"><img src="https://github.com/nikhilxsunder/edgar-sec/actions/workflows/codeql.yml/badge.svg" alt="CodeQL"></a>
    <a href="https://www.bestpractices.dev/projects/10210"><img src="https://www.bestpractices.dev/projects/10210/badge"></a>
    <a href="https://codecov.io/gh/nikhilxsunder/edgar-sec"><img src="https://codecov.io/gh/nikhilxsunder/edgar-sec/graph/badge.svg?token=RDI3Q99UJB" alt="codecov"></a>
    <a href="https://socket.dev/pypi/package/edgar-sec/overview/2.0.0/tar-gz"><img src="https://socket.dev/api/badge/pypi/package/edgar-sec/2.0.0?artifact_id=tar-gz"></a>
    <a href="https://repology.org/project/python%3Afedfred/versions"><img src="https://repology.org/badge/tiny-repos/python%3Afedfred.svg" alt="Packaging status"></a>
    <a href="https://pypi.org/project/edgar-sec/"><img src="https://img.shields.io/pypi/v/edgar-sec.svg" alt="PyPI version"></a>
    <a href="https://pepy.tech/projects/edgar-sec"><img src="https://static.pepy.tech/badge/edgar-sec" alt="PyPI Downloads"></a>
    <a href="https://anaconda.org/conda-forge/edgar-sec"><img src="https://img.shields.io/conda/vn/conda-forge/edgar-sec.svg" alt="Conda-Forge Version"></a>
    <a href="https://anaconda.org/conda-forge/edgar-sec"><img src="https://img.shields.io/conda/dn/conda-forge/edgar-sec.svg" alt="Conda Downloads"></a>
</div>

### Features

- Now available on Conda-Forge!
- Native support for asynchronous requests (async).
- All method outputs are mapped to dataclasses for better usability.
- Local caching for easier data access and faster execution times.
- Built-in rate limiter that doesn't exceed 10 calls per second (ignores local caching).
- MyPy compatible type stubs.

### Installation

You can install the package using pip:

```sh
pip install edgar-sec
```

Or install from conda-forge:

```sh
conda install -c conda-forge edgar-sec
```

For type checking support, install with optional type stubs:

```sh
pip install edgar-sec[types]
```

We recommend using a virtual environment with either installation method.

### Rest API Usage

I recommend consulting the documentation at:
https://nikhilxsunder.github.io/edgar-sec/

Here is a simple example of how to use the package:

```python
# EDGAR API
import edgar_sec as ed
edgar = ed.EdgarAPI()

# Get company concept disclosures
company_concept = edgar.get_company_concept(central_index_key='0001067983', taxonomy='us-gaap', tag='AccountsPayableCurrent')
print(company_concept.label)

# Get company concept disclosures (async)
import asyncio
async def main():
    edgar = ed.EdgarAPI().Async
    company_concept = await edgar.get_company_concept(central_index_key='0001067983', taxonomy='us-gaap', tag='AccountsPayableCurrent')
    print(company_concept.label)
asyncio.run(main())
```

### Continuous Integration

Edgar-SEC uses GitHub Actions for continuous integration. The following workflows run automatically:

- **Build and Test**: Triggered on every push and pull request to verify the codebase builds and tests pass
- **Analyze**: Runs static code analysis to identify potential issues
- **Test**: Comprehensive test suite with coverage reporting
- **CodeQL**: Security analysis to detect vulnerabilities
- **Docs**: Deploys Sphinx docs site to Github Pages.

These checks ensure that all contributions maintain code quality and don't introduce regressions.

Status badges at the top of this README reflect the current state of our CI pipelines.

### Development

Edgar-SEC uses standard Python packaging tools:

- **Poetry**: For dependency management and package building
- **pytest**: For testing
- **Sphinx**: For documentation generation

To set up the development environment:

```sh
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clone the repository
git clone https://github.com/nikhilxsunder/edgar-sec.git
cd edgar-sec

# Install dependencies
poetry install

# Run tests
poetry run pytest
```

### Testing

The project uses pytest as its testing framework. Tests are located in the `tests/` directory.

To run the complete test suite:

```sh
poetry run pytest
```

For running tests with coverage reports:

```sh
poetry run pytest --cov=edgar_sec tests/
```

To run a specific test file:

```sh
poetry run pytest tests/specific_module_test.py
```

#### Test Coverage

We aim to maintain a minimum of 80% code coverage across the codebase. This includes:

- Core functionality: 90%+ coverage
- Edge cases and error handling: 80%+ coverage
- Utility functions: 75%+ coverage

Continuous integration automatically runs tests on all pull requests and commits to the main branch.

#### Test Policy

Edgar-SEC requires tests for all new functionality. When contributing:

- All new features must include appropriate tests
- Bug fixes should include tests that verify the fix
- Tests should be added to the automated test suite in the `tests/` directory

## Security

For information about reporting security vulnerabilities in Edgar-SEC, please see our [Security Policy](https://github.com/nikhilxsunder/edgar-sec/blob/main/SECURITY.md).

### Contributing

Contributions are welcome! Please open an issue or submit a pull request.

### License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](https://github.com/nikhilxsunder/edgar-sec/blob/main/LICENSE) file for details.
