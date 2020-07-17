============
Installation
============

Get TaxTea
---------------------

Install Django TaxTea:

.. code-block:: bash

    pip install django-taxtea

Configuration
---------------

Add ``django-taxtea`` to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS =(
        ...
        "taxtea",
        ...
    )


Add required settings:

.. code-block:: python

    TAXTEA_USPS_USER = os.environ.get("TAXTEA_USPS_USER", "<your usps user>")
    TAXTEA_AVALARA_USER = os.environ.get("TAXTEA_AVALARA_USER", "<your avalara user>")
    TAXTEA_AVALARA_PASSWORD = os.environ.get("TAXTEA_AVALARA_PASSWORD", "<your avalara password>")
    TAXTEA_NEXUSES = [("AZ", "12345"),] 
    TAXTEA_TAX_RATE_INVALIDATE_INTERVAL = 7  # Optional, default is 7 (days)

Migrate the Database::

    python manage.py migrate

Running Tests::

    python manage.py test
