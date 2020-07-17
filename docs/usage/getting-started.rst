Getting Started
================


Required Accounts
-----------------
A USPS Web Service API account and an Avalara API account are required for TaxTea to work. Both of
these are free and their registration links are below. 

`USPS <https://www.usps.com/business/web-tools-apis/>`_
- Provides TaxTea a method for retrieving a State from a Zip Code.

`Avalara <https://developer.avalara.com/api-reference/avatax/rest/v2/methods/Free/RequestFreeTrial/>`_
- Provides TaxTea up-to-date tax rates for Zip Codes.

.. note:: Make sure these are in your django settings as noted in the installation page before proceeding.


Typical Usage
-------------

A simple flow for using TaxTea looks like this.

.. code-block:: python

    from taxtea.models import ZipCode

    # Get the ZipCode Object from the database
    # If no object exists for this Zip Code, it will create one by 
    # fetching data from the USPS API and storing it in the database.
    # At this point, there will be no `tax_rate` associated with it.

    zip_code = ZipCode.get("90210")

    # The `applicable_tax_rate` property is the workhorse of TaxTea.
    # It will fetch & store a tax rate from the Avalara API and then
    # use your tax nexuses to determine which tax rate is applicable.

    tax_rate = zip_code.applicable_tax_rate
    # Returns a Decimal object that will look like `0.0625`

    # For convenience, there is a classmethod to convert to a percent.

    percentage = ZipCode.tax_rate_to_percentage(tax_rate)
    # Returns a Decimal object that will look like `6.25`
