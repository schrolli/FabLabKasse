# FabLabKasse
FabLabKasse, a Point-of-Sale Software for FabLabs and other public and trust-based workshops

# Getting started

See INSTALLING for detailed instructions on how to install the required dependencies. You can skip the configuration stuff for later.

Please checkout the repository recursively since it contains submodules:

`git clone --recursive git@github.com:fau-fablab/FabLabKasse.git`

Then, for the first try, you can just do:

`./run.py --example`


Have fun and give feedback!

# Testing features without real hardware

(assuming the example config settings)

- automated cash payment: uncomment the device1_... example entries in config.ini to add a simulated cash device accepting and dispensing 10€ notes randomly
- receipt printing: run `./tools/dummy-printserver` to roughly see how a receipt printer's output would look [please note that receipt printing is not yet implemented on all shopping backends]

# Debugging

for a graphical winpdb debugger, start:
`./run.py --debug`
and click "continue" a few times

# Code structure overview

- run.py is the launcher, it starts FabLabKasse/gui.py
- the rest of the code is in folder FabLabKasse
- kassenbuch.py (currently still german) accounting CLI for legacy_offline_kassenbuch shopping backend
- produkt.py is directly in FabLabKasse-folder for legacy reasons
- cashPayment: automated cash payment - coin and banknote acceptors. see README.cashPayment
  - client: interface towards the GUI that connects with the device drivers
     - PaymentDevicesManager: manages all (multiple) payment devices, used by the GUI (as self.cashPayment)
     - PaymentDeviceClient: one device used by PaymentDevicesManager, launches a 'server' process and communicates with it via the protocol specified in cashPayment/protocol.txt
  - server: device drivers. they run as a standalone process
    - cashServer: abstract base class
    - exampleServer: simulated hardware for first tests
    - nv11, mdbCoinChanger: real hardware
  - protocol.txt: specification of how client (GUI) and server (individual device-driver process) communicate
  - cashState: database backend + CLI for accounting cash (individual pieces of money) inside the devices. This accounting is for auditing and error-finding purposes and therefore separate from the shopping backend, which has its own accounting (that does not look at individual coins, but just at sums). management tool can be started as ./cash from the main directory
  - listSerialPorts: tool to list all ports that can be found with pyserial, useful for configuration of all (usb-)serial connecting device drivers
- shopping: 
  - backend: backends that provide connection to a webshop, ERP system, database etc and manages products, categories, carts and financial accounting (storage of payments)
    - abstract: abstract base class
    - offline_base: abstract base class for backends that read products only once at the start and keep the cart in memory; as opposed to a always-online system that has its whole state somewhere in the cloud
    - dummy: has some fake products, just silently accepts all payments without storing them somewhere
    - oerp: OpenERP / odoo implementation, still needs testing.
    - legacy_offline_kassenbuch: backend with product importing from a python script, SQLite based double-entry bookkeeping, contains many german database field names and is therefore marked as legacy. With some re-writing it would make a decent SQLite backend. Has a management CLI kassenbuch.py in the main folder.
  - payment_methods: different methods of payment like manual cash entry, automatic cash in+output, charge on client account, ...
- libs: some helping libraries
- produkte: empty directory for local caching of product data (TODO rename)
- scripts: some helping cronjobs
  - TODO

# Code style guide

All contributions should have a good coding style:

## Low level (formatting, docs)

- Run pylint and fix all warnings and errors (except line length) as far as possible.
- Follow the conventions set in PEP8, except that a longer line length is okay if it helps readability
  - to fix whitespace, you can use `autopep8 --in-place --max-line-length=9999 $file"
- write reStructuredText formatted function docstrings, example:
```
def do_something(value):
    """
    do something magic with value

    :return: True if the sun shines tomorrow, False otherwise
    :rtype: bool
    :param value: your telephone number
    :type value: unicode
    """
```

- for the docstrings, use the type syntax as defined at https://www.jetbrains.com/pycharm/help/type-hinting-in-pycharm.html#d301935e18526

## High level (structure)

- Make your code modular, reusable and well-documented. Not only for others, but also for your future self.
- Use enough assertions in all code that has to do with money (payment, accounting, etc.).
- For signaling errors, prefer Exceptions to return codes.
- Avoid print, use logging.info, logging.warning etc. because these are automatically saved to a logfile

# Contributing

- This project is available under GPLv3 (see file `LICENSE`)
- Follow the Code style guide
- Develop features in a separate branch, rebasing into logically divided commits is encouraged
- Please no fast-forward-merging (use `git merge --no-ff`, standard behaviour of Github pull requests)
- [This article](http://nvie.com/posts/a-successful-git-branching-model/) propagates a similar model
