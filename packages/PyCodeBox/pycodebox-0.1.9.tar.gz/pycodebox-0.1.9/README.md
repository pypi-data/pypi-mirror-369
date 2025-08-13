# PyCodeBox

[![Python Tests](https://github.com/zwallen/PyCodeBox/actions/workflows/python-tests.yml/badge.svg)](https://github.com/zwallen/PyCodeBox/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/zwallen/PyCodeBox/branch/master/graph/badge.svg)](https://codecov.io/gh/zwallen/PyCodeBox)
[![PyPI version](https://img.shields.io/pypi/v/PyCodeBox.svg)](https://pypi.org/project/PyCodeBox/)

A personal collection of Python convenience functions for styling data displays and outputs, transforming and organizing data, performing statistical analyses, and other commonly performed actions in data science projects.

Releases of the package can be installed from PyPI:

```bash
pip install pycodebox
```

or development versions (which may or may not line up with official releases) from GitHub:

```bash
pip install git+https://github.com/zwallen/PyCodeBox.git
```

And imported in your Python scripts as follows:

```python
from pycodebox import export_styled_xlsx_w_2_headers, fisher_exact_by_strata
```

## Important Disclaimer

As these are only personal convenience functions wrapping existing functions and packages:

* **Compatibility:** They may or may not work for your purposes as they were designed in response to specific workflows and analyses. They are not meant to be designed for general audience use.
* **Support:** Limited support is provided - use at your own risk and test thoroughly with your data.
* **Citation:** Citation of the package is not necessary if you decide to use any of the functions written here (but glad if they were able to help!).

## Issues and Contributing

This is primarily a personal package, but if you encounter bugs or have suggestions:
* Open an issue on GitHub for bug reports
* Pull requests are welcome for bug fixes
* For questions, contact: zachary.d.wallen@gmail.com

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

Version 0.1.8 (current)
* Added function `pca_kmeans_plot` and corresponding testing of function to perform PCA and K-means clustering, returning a plot of the results and a contingency table if a known group variable is provided

Version 0.1.7
* Added function `read_tab_delim_file_to_dict` to read a tab-delimited file line by line to a dictionary (useful for files that do not have the same number of fields per row)

Version 0.1.6
* Converted plotting functions to use `matplotlib` and `seaborn` instead of `plotnine`
* Added statistical testing and plotting of significant associations to `stratified_barplot` and `stratified_violin_boxplot` functions
* Fixed docstrings of all functions so they render correctly

Version 0.1.5
* Added stratified volcano plot function and associated testing

Version 0.1.3
* Fixed spacing issues and fine tuned plotting functions
* Updated docstrings across functions

Version 0.1.2
* Updated plotting functions to be more dynamic in some of the text placement
* Updated testing of plotting functions to include both required only and full parameter testing

Version 0.1.1
* Updated package name to `pycodebox` to avoid conflicts with existing packages on PyPI
* Successful upload to PyPI, so package can now be installed via `pip install pycodebox`

Version 0.1.0
* Initial release
* Basic data styling, transformation, statistical analysis, and plotting functions

---
**Note:** This package represents a personal toolkit developed for specific analytical needs. While shared publicly, it prioritizes the author's workflows over general usability.
