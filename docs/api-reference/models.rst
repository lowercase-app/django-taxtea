Models
======

Models hold the bulk of the functionality included in the django-taxtea package.
It is recommended to always fetch a ZipCode via the ``.get()`` method, as it will
perform get or create actions to ensure a ZipCode is returned. 
It is also recommended to use the ``applicable_tax_rate`` property to get the tax rate
for a given ZipCode. The ``tax_rate`` property of the model only stores the general tax rate
a Zip Code charges, this can be different than what tax rate needs to be charged based on a
company's Tax Nexuses and whether the State(s) involved are ``ORIGIN`` or ``DESTINATION based``.



State
-----
.. autoclass:: taxtea.models.State


.. automethod:: taxtea.models.State.state_for_zip

ZipCode
-------
.. autoclass:: taxtea.models.ZipCode
   :members: applicable_tax_rate

.. automethod:: taxtea.models.ZipCode.tax_rate_to_percentage
.. automethod:: taxtea.models.ZipCode.get
.. automethod:: taxtea.models.ZipCode.nexuses
.. automethod:: taxtea.models.ZipCode.refresh_rates
.. automethod:: taxtea.models.ZipCode.validate