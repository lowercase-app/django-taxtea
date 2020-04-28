# TaxTea

Django Tax App for SaaS.

Taxes are hard. That shouldn't stop you from building your dreams. TaxTea does the heavy lifting and tells you exactly what sales tax, if any, you need to be charging your customers.

> Currently only supporting US 🇺🇸

## Installation

```
poetry add git+https://github.com/lowercase-app/taxtea.git#latest
```

## Getting Started

Add the following to your django settings:

```python
TAXTEA_USPS_USER = "XXXXXXXX" # required
TAXTEA_AVALARA_USER = "XXXXXXXX" # required
TAXTEA_AVALARA_PASSWORD = "XXXXXXXX" # required
TAXTEA_NEXUSES = [("AZ", "12345"),] # required
TAXTEA_TAX_RATE_INVALIDATE_INTERVAL = 7 # optional, default is 7 (days)
```

### USPS

TaxTea uses the USPS web service api to find states for zip codes. You'll need to register for a free account [here.](https://www.usps.com/business/web-tools-apis/)
NOTE: TaxTea only needs the USPS user, not the password.

### Avalara

TaxTea relies on Avalara for getting up-to-date tax rates for Zip Codes. The Avalara website can be confusing, but to register simply hit the API end point documented [here.](https://developer.avalara.com/api-reference/avatax/rest/v2/methods/Free/RequestFreeTrial/)

### Nexuses

Your `TAXTEA_NEXUSES` are any place where your company has a presence. For example, every company has a nexus where they incorporated. We require there to be at least one item in this list, which is your physical incorporation state/zip.

Nexuses are part of the equation of how TaxTea calculates sales tax. There are two types of sales tax -- Origin and Destination. Origin means that the sales tax will be collected from the state where you have a nexus. For example, if your incorporation state is an Origin-based state and a customer purchases your product who also lives in that state, it is the nexus' zip code that gets used to determine the tax rate, not the customer's.  Destination-based sales tax means that the sales tax will be charged at the rate of where the customer lives. This is applicable for out of state transactions and transactions within a state that is not an Origin-based. Want to learn more? Here's great article about [Origin vs. Destination-based Sales tax](https://blog.taxjar.com/charging-sales-tax-rates/) from Tax Jar.


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

Import the core function:

```python
from taxtea.utils import get_tax_rate_for_zipcode
```
### Function Spec
**Name** `get_tax_rate_for_zipcode()`

**Parameters**

| Name          | Type | Required | Default | Description                                                                                                                          
|---------------|------|----------|---------|-------------|
| zipcode       | str  | yes      | n/a     | The zipcode you wish to look up                                                                                                        |
| return_always | bool | no       | False   | Always return a tax rate, even when no tax needs to be collected                                                                       |
| force         | bool | no       | False   | Force a check for a new tax rate. Tax rates are refreshed (upon request) according to the `TAXTEA_TAX_RATE_INVALIDATE_INTERVAL` setting. |

**Return** `type: float`

Function will return `0.00` if the state does not collect sales tax for SaaS. 
>**NOTE**: If the given Zip Code is in a state where you hold a nexus and that state is an ORIGIN-based sales tax state, the returned tax rate will be for the Zip Code of the nexus.


### Signals
TaxTea implements a single Signal to allow you to perform tasks when a Zip Code's tax rate has changed.

```python
from django.dispatch import receiver
from taxtea.signals import tax_rate_changed

@receiver(tax_rate_changed)
def my_callback(sender, instance, **kwargs):
    print(f"ZipCode {instance.code} new tax rate => {instance.tax_rate}")
    print("Do some work...")
```

**Parameters**

| Name     | Type    | Description                                  |
|----------|---------|----------------------------------------------|
| sender   | ZipCode | The ZipCode class                            |
| instance | ZipCode | The ZipCode instance that has a new tax rate |

