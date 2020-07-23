<h1 align="center">TaxTea</h1>

<div align="center">
  <strong>Django app that calculates tax rates for SaaS products :frog::tea:</strong>

</div>

<div align="center">
  <sub>A little package that goes a long way. Built by
  <a href="https://twitter.com/matt_strayer">Matt Strayer</a> and
  <a href="https://github.com/lowercase-app/django-taxtea/graphs/contributors">
    contributors
  </a>
  </sub>
</div>

<br />

<div align="center">
  <!-- Stability -->
  <a href="https://pypi.python.org/pypi/django-taxtea/">
    <img src="https://img.shields.io/pypi/status/django-taxtea.svg?style=flat-square"
      alt="Stability" />
  </a>
  <!-- Version -->
  <a href="https://pypi.python.org/pypi/django-taxtea/">
    <img src="https://img.shields.io/pypi/v/django-taxtea.svg?style=flat-square"
      alt="PyPi version" />
  </a>

  <!-- Python Support -->
  <a href="https://pypi.python.org/pypi/django-taxtea/">
    <img src="https://img.shields.io/pypi/pyversions/django-taxtea.svg?style=flat-square"
      alt="Python Support" />
  </a>
  <!-- License -->
  <a href="https://pypi.python.org/pypi/django-taxtea/">
    <img src="https://img.shields.io/pypi/l/django-taxtea.svg?style=flat-square"
      alt="License" />
  </a>
  <!-- Sponsored -->
  <a href="https://www.lowercase.app/">
    <img src="https://img.shields.io/badge/Sponsored_By-lowercase-a463f2.svg?style=flat-square"
      alt="Sponsored By" />
  </a>
</div>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Purpose](#purpose)
- [Features](#features)
- [Installation](#installation)
- [Settings](#settings)
- [Required Accounts & Information](#required-accounts--information)
  - [USPS](#usps)
  - [Avalara](#avalara)
  - [Nexuses](#nexuses)
- [Usage](#usage)
- [Example](#example)
- [Documentation](#documentation)
- [Resources](#resources)

## Purpose

Taxes are hard, but that shouldn't stop you from building your dreams. When building [lowercase](https://www.lowercase.app), we found out just how hard calculating the _right_ sales tax rate is. Thus, TaxTea was born. TaxTea does the heavy lifting, and tells you exactly what sales tax, if any, you need to charge your customers. So, sit back, sip some tea, and channel your inner [Kermit](https://i.kym-cdn.com/entries/icons/original/000/015/878/thatsnoneofmy.jpg) because tax rates are none of your business...anymore!

> Currently only supporting US 🇺🇸


## Features

- __Simple API:__ Get up & running in minutes.
- __Tax Nexuses, Origin, & Destination Support:__ The three factors in calculating tax rates. TaxTea handles them all expertly.
- __Up-to-date:__ No more fear of charging a wrong tax rate. TaxTea is always up to date.


## Installation

```bash
pip install django-taxtea
```

## Settings

Add the following to your Django settings:

```python
TAXTEA_USPS_USER = "XXXXXXXX"           # required
TAXTEA_AVALARA_USER = "XXXXXXXX"        # required
TAXTEA_AVALARA_PASSWORD = "XXXXXXXX"    # required
TAXTEA_NEXUSES = [("AZ", "12345"),]     # required
TAXTEA_TAX_RATE_INVALIDATE_INTERVAL = 7 # optional, default is 7 (days)
```

## Required Accounts & Information

### USPS

TaxTea uses the USPS web service API to find states for Zip Codes. You'll need to register for a free account [here.](https://www.usps.com/business/web-tools-apis/)

**NOTE: TaxTea only needs the USPS user, not the password.**

### Avalara

TaxTea relies on Avalara for getting up-to-date tax rates for Zip Codes. The Avalara website can be confusing, but to register simply hit the API endpoint documented [here.](https://developer.avalara.com/api-reference/avatax/rest/v2/methods/Free/RequestFreeTrial/)

### Nexuses

Your `TAXTEA_NEXUSES` are any place where your company has a presence. For example, every company has a nexus where they incorporated. We require there to be at least one item in this list, which is your physical incorporation state/zip.

Nexuses are part of the equation of how TaxTea calculates sales tax.

The determination of [sales tax sourcing](https://www.avalara.com/us/en/blog/2019/02/sales-tax-sourcing-how-to-find-the-right-rule-for-every-transaction.html) is predicated on whether a given state's model for taxation is:

- Origin-based, or
- Destination-based

For example, if your incorporation state is an _Origin-based_ state and a customer purchases your product who also lives in that state, it is the nexus' Zip Code that is used to determine the tax rate, not the customer's location.

_Destination-based_ sales tax means that the sales tax will be charged at the rate of the customer location. This is applicable for out of state transactions and transactions within a state that is not an Origin-based.

Want to learn more? Here's a great article about [Origin vs. Destination-based Sales tax](https://blog.taxjar.com/charging-sales-tax-rates/) from Tax Jar.

## Usage

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "taxtea"
]
```

Run migrations:

```python
python manage.py migrate
```

## Example

Import the ZipCode model:

```python
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

```

## Documentation

Read the [documentation](https://www.djangotaxtea.com).


## Resources

TaxTea uses a list provided by taxjar to populate the states and their tax collection methods.

- [SaaS Sales Tax](https://blog.taxjar.com/saas-sales-tax/)
- [Origin / Destination States](https://blog.taxjar.com/charging-sales-tax-rates/)
