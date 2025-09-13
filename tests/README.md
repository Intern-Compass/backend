## To Run Tests

To run the full test suite and ensure everything is working correctly:

```bash
python -m pytest
```

## To Run with Code Coverage

To run the tests with code coverage and see how much of the code is being tested:

```bash
coverage run -m pytest

coverage report
```

This command creates a detailed, interactive HTML report in a new directory called htmlcov:

```bash
coverage html
```

Open the main `index.html` file in your browser to see a color-coded view of the code with covered lines in green and missed lines in red.
