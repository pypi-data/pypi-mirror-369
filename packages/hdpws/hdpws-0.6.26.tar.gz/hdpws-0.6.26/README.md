
## Synopsis

This library provides a simple python interface to 
NASA's [Heliophysics Data Portal's](https://heliophysicsdata.gsfc.nasa.gov/)
(HDP) Space Physics Archive, Search, and Extract 
([SPASE](https://spase-group.org/)) Web Service.  This library implements 
the client side of the 
[HDP RESTful web services](https://heliophysicsdata.gsfc.nasa.gov/WebServices/).
For more general details about the HDP web services, see
https://heliophysicsdata.gsfc.nasa.gov/WebServices/.
![SPASE Inside](https://spase-group.org/assets/images/spase-inside.png)

## Code Example

This package contains example code calling most of the available web services.
To run the included example, do the following

    python -m hdpws

---

Also, the following [Jupyter notebooks](https://jupyter.org/) demonstrate
different features of the library:
1. [Simple Query Example](https://heliophysicsdata.gsfc.nasa.gov/WebServices/jupyter/HdpWsExample.html) ([ipynb file](https://heliophysicsdata.gsfc.nasa.gov/WebServices/jupyter/HdpWsExample.ipynb)) demonstrating a simple query. [Launch on Binder](https://mybinder.org/v2/gh/berniegsfc/hdpws-notebooks/main?labpath=HdpWsExample.ipynb).
2. [Example with data retrieval](https://heliophysicsdata.gsfc.nasa.gov/WebServices/jupyter/HdpWsExampleWithCdasWs.html) using [cdasws](https://pypi.org/project/cdasws/) ([ipynb file](https://heliophysicsdata.gsfc.nasa.gov/WebServices/jupyter/HdpWsExampleWithCdasWs.ipynb)).  [Launch on Binder](https://mybinder.org/v2/gh/berniegsfc/hdpws-notebooks/main?labpath=HdpWsExampleWithCdasWs.ipynb).


## Motivation

This library hides the HTTP and JSON/XML details of the HDP web 
services. A python developer only has to deal with python objects and 
methods.

## Dependencies

At this time, the only dependency are:
1. [requests](https://pypi.org/project/requests/)

The critical dependencies above will automatically be installed when this 
library is.

## Installation

To install this package

    $ pip install -U hdpws

## API Reference

Refer to
[hdpws package API reference](https://heliophysicsdata.gsfc.nasa.gov/WebServices/py/hdpws/index.html)

or use the standard python help mechanism.

    from hdpws import HdpWs
    help(HdpWs)

## Tests

The tests directory contains 
[unittest](https://docs.python.org/3/library/unittest.html)
tests.

## Contributors

Bernie Harris.  
[e-mail](mailto:NASA-SPDF-Support@nasa.onmicrosoft.com) for support.

## License

This code is licensed under the 
[NASA Open Source Agreement](https://cdaweb.gsfc.nasa.gov/WebServices/NASA_Open_Source_Agreement_1.3.txt) (NOSA).
