# sapioseleniumlib: Official Sapio Selenium End-to-End Testing Library

<div align="center"><a href="https://www.sapiosciences.com" target="_blank">
  <img src="https://public.exemplareln.com/sapio-pylib/sapio_selenium_python_library_header_image.png" alt="Sapio Sciences"><br>
</a></div>

-----------------
[![PyPI Latest Release](https://img.shields.io/pypi/v/sapioseleniumlib.svg)](https://pypi.org/project/sapiopylib/) [![License](https://img.shields.io/pypi/l/sapioseleniumlib.svg)](https://github.com/sapiosciences/sapio-py-tutorials/blob/master/LICENSE)


## What is it?

This is a library that can be used to support selenium end-to-end testing.
You can write end-to-end testing script using the classes we have here.

There is also an example of TruSeq DNA from Blood ELN workflow testing class available within the package.
That can be used as a reference as you write your own script.

The library includes both Sapio Platform supporting Project-Object models and Sapio Foundations.

We use this library ourselves before releasing the platform to run automated tests.
Therefore, we may publish releases of the library that may not have been made generally available. 
These releases are marked as "pre-release" with Alpha, Beta, or Release-Candidate version format.

## Where to get it
Installation is simple:
```sh
pip install sapioseleniumlib
```

However, you may need to pay attention to the library version to ensure it is compatible with your Sapio Informatics Platform.

Since we continue to make user interface changes from version to version in Sapio Platform, it can be a good idea to synchronize the library version whenever your system has been upgraded to a new major release.

If you would like to keep multiple versions of this library for different versions of Sapio Platform among dev/staging/prod stacks, consider using anaconda, miniconda, or venv.

It is also possible that the library needs an update as browser technologies develop. If a popular supported browser had been released that is no longer compatible with the library, we may choose to release another version for the same Sapio Platform.

## Licenses
This library are licensed under MPL 2.0. 

pypi.org is granted the right to distribute sapioseleniumlib forever.

This license does not provide any rights to use any other copyrighted artifacts from Sapio Sciences. (And they are typically written in another programming language with no linkages to this library.)

## Dependencies
The following dependencies are required for this package:
- [selenium - Selenium automates browsers. That's it!](https://pypi.org/project/selenium)
- [webdriver-manager - Library provides the way to automatically manage drivers for different browsers](https://pypi.org/project/webdriver-manager)


## Getting Help
If you have support contract with Sapio Sciences, please use our [technical support channels](https://sapio-sciences.atlassian.net/servicedesk/customer/portals).

If you have any questions about how to use sapiopylib, please visit our tutorial page.

If you would like to report an issue on sapiopylib, or its tutorial content, please feel free to create a issue ticket at the tutorial github.

## About Us
Sapio is at the forefront of the Digital Lab with its science-aware platform for managing all your life science data with its integrated Electronic Lab Notebook, LIMS Software and Scientific Data Management System.

Visit us at <a href="https://www.sapiosciences.com">Sapio Sciences</a>