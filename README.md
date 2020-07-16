# Django TaxTea

Django Tax App for SaaS.

Taxes are hard. That shouldn't stop you from building your dreams. TaxTea does the heavy lifting and tells you exactly what sales tax, if any, you need to be charging your customers.

> Currently only supporting US 🇺🇸

## Installation

```bash
pip install django-taxtea
```

## Getting Started

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

## Getting Tax Rates

Import the ZipCode model:

```python
from taxtea.models import ZipCode
```

## Resources

TaxTea uses a list provided by taxjar to populate the states and their tax collection methods.

- [SaaS Sales Tax](https://blog.taxjar.com/saas-sales-tax/)
- [Origin / Destination States](https://blog.taxjar.com/charging-sales-tax-rates/)

## Model Spec

## ZipCode

### Class Method `get()`

**Parameters**

| Name    | Type | Required | Default | Description            |
| ------- | ---- | -------- | ------- | ---------------------- |
| zipcode | str  | yes      | n/a     | The zipcode to look up |

**Return** `type: ZipCode`

### Class Method `tax_rate_to_percentage()`

**Parameters**

| Name     | Type    | Required | Default | Description                              |
| -------- | ------- | -------- | ------- | ---------------------------------------- |
| tax_rate | Decimal | yes      | n/a     | Tax Rate to be converted: Example `0.06` |

**Return** `type: Decimal`

### Property `applicable_tax_rate`

**Return** `type: Decimal`

### Class Method `nexuses()`

**Parameters**

> None

**Return** `type: [ZipCode]`

### Property `applicable_tax_rate`

**Return** `type: Decimal`

The function will return `0.00` if the state does not collect sales tax for SaaS.

> **NOTE**: If the given Zip Code is in a state where you hold a nexus and that state is an ORIGIN-based sales tax state, the returned tax rate will be for the Zip Code of the nexus.

## State

### Class Method `state_for_zip()`

**Parameters**

| Name    | Type | Required | Default | Description            |
| ------- | ---- | -------- | ------- | ---------------------- |
| zipcode | str  | yes      | n/a     | The zipcode to look up |

**Return** `type: State`
