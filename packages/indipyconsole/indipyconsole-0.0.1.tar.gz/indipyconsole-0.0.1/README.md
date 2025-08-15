# indipyconsole

You may have Python programs implementing some form of data collection or control and wish to remotely operate such an instrument.

An associated package 'indipydriver' can be used to take your data, organise it into a data structure defined by the INDI protocol, and serve it on a port.

This indipyconsole package provides a terminal client, which connects to the port, allowing you to view and control your instrument from a terminal session.

A further package indipyterm is also available, by the same author, which you may prefer.

indipyterm can run on other OS's apart from Linux, and gives a more attractive terminal output, however it depends on third party libraries.

indipyconsole only depends on indipyclient - which provides the communication methods. It uses the Python standard library curses package, which is only available on Linux.

The main purpose of indipyconsole is to provide an indipendent client, in case the third party packages used by indipyterm break. It also provides logging capabilities to save communications data to a logfile. The two clients can both connect to an INDI server to compare output.

indipyconsole can be installed from Pypi with:

pip install indipyconsole

or if you use uv, it can be loaded and run with:

uvx indipyconsole

indipydriver and indipyconsole communicate with the INDI protocol.

INDI - Instrument Neutral Distributed Interface.

See https://en.wikipedia.org/wiki/Instrument_Neutral_Distributed_Interface

The INDI protocol defines the format of the data sent, such as light, number, text, switch or BLOB (Binary Large Object). The client is general purpose, taking the format of switches, numbers etc., from the protocol.

The client can be run from a virtual environment with

indipyconsole [options]

or with

python3 -m indipyconsole [options]

The package help is:

    usage: indipyconsole [options]

    Console client to communicate to an INDI service.

    options:
      -h, --help                show this help message and exit
      -p PORT, --port PORT      Port of the INDI server (default 7624).
      --host HOST               Hostname/IP of the INDI server (default localhost).
      -b BLOBS, --blobs BLOBS   Optional folder where BLOB's will be saved.
      --loglevel LOGLEVEL       Enables logging, value 1, 2, 3 or 4.
      --logfile LOGFILE         File where logs will be saved
      --version                 show program's version number and exit

    The BLOB's folder can also be set from within the session.
    Setting loglevel and logfile should only be used for brief
    diagnostic purposes, the logfile could grow very big.
    loglevel:1 Information and error messages only, no exception trace.
    The following levels enable exception traces in the logs
    loglevel:2 As 1 plus xml vector tags without members or contents,
    loglevel:3 As 1 plus xml vectors and members - but not BLOB contents,
    loglevel:4 As 1 plus xml vectors and all contents


If installed from Pypi, then the dependecy indipyclient will automatically be pulled and installed.

The indipydriver package which can be used to create instrument control, and serve the INDI protocol is available at:

https://pypi.org/project/indipydriver

https://github.com/bernie-skipole/indipydriver

https://indipydriver.readthedocs.io

With example driver scripts at:

https://github.com/bernie-skipole/inditest

The indipyterm package is available at:

https://pypi.org/project/indipyterm

https://github.com/bernie-skipole/indipyterm

The indipyclient package contains classes which may be useful if you want to create your own client or client script:

https://pypi.org/project/indipyclient

https://github.com/bernie-skipole/indipyclient

https://indipyclient.readthedocs.io
