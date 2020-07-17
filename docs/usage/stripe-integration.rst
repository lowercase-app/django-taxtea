==================
Stripe Integration
==================


`lowercase <https://www.lowercase.app/>`_ uses TaxTea integrated with Stripe to handle our tax collection. Here we'll 
go through how to set up TaxTea to work with Stripe.


Overview
--------


#. Capture Zip Code from Stripe Payment Method

#. Use TaxTea to get what Tax Rate you need to charge for the Zip Code

#. Create a ``Tax Rate`` in Stripe

#. Update Customer's Subscription



Capture Zip Code
----------------

First things first, we need the `Payment Method <https://stripe.com/docs/api/payment_methods/object>`_ that your customer
uses to pay for their subscription. There are a few different ways you can get this data. But for this example we'll be using a Stripe
Webhook event. 

We want to keep the Tax Rate in sync with the customer's default payment method, so we'll listen to the ``customer.updated`` event
which will provide us a `Customer Object <https://stripe.com/docs/api/customers/object>`_ in the webhook's data payload.



.. code-block:: Python

    import stripe

    # stripe_data is the contents of the `data` object in the webhook JSON payload
    customer_object = stripe_data.get("object")

    # use the walrus operator (Python 3.8) to store the id of `default_payment_method`
    # if it exists
    if d := data.get("invoice_settings").get("default_payment_method"):
        # Fetch the full payment method details via the stripe api
        payment_method = stripe.PaymentMethod.retrieve(d)
        # Traverse the Stripe Object to get the `postal_code`
        # "billing_details": {
        #     "address": {
        #         "city": null,
        #         "country": null,
        #         "line1": null,
        #         "line2": null,
        #         "postal_code": "42424",
        #         "state": null
        #         },
        #     "email": "jenny@example.com",
        #     "name": null,
        #     "phone": "+15555555555"
        # }
        zip_code = payment_method.billing_details.address.postal_code
        # Save this Zip Code somewhere. In a user's settings, etc. 
        # We'll need it later


.. note::
    There are some cards that do not require a Zip Code. You can ensure that your customers use a payment method that 
    has a Zip Code by enabling the ``Block if ZIP code everification fails`` `Radar Rule <https://stripe.com/docs/radar/rules#traditional-bank-checks>`_




TaxTea Magic 🧙‍♂️
------------------


.. code-block:: Python

    from taxtea.models import ZipCode

    zip_code = ZipCode.get("{{Zip Code From above}}")
    tax_rate = zip_code.applicable_tax_rate
    percentage = ZipCode.tax_rate_to_percentage(tax_rate)

Create Stripe Tax Rate
-----------------------

Before we update a subscription, we need to make sure that we have a `Tax Rate Object <https://stripe.com/docs/api/tax_rates/object>`_ in Stripe for this Zip Code. 


.. code-block:: Python

    import stripe
    # You can get tax rates from stripe in batches of 100. You'll
    # need to traverse the returned objects to see if any have a
    # description equal to the Zip Code you're working with above. 
    
    # Will look something like this...
    tax_rates = stripe.TaxRate.list(limit=100, active=True)
    match = False
    for tax_rate in tax_rates.data:
        if tax_rate == zip_code:
            match = True
            # use this this tax rate
    if not match:
        # Tax Rate doesn't exist, create it.

    # If your application uses dj-stripe, then the above logic is a lot easier
    # and looks like this.
    from django.core.exceptions import ObjectDoesNotExist
    from djstripe.models import TaxRate

    try:
        tax_rate = TaxRate.objects.get(description=zip_code, active=True)
    except ObjectDoesNotExist:
        # Tax Rate doesn't exist, create it.

    ###################
    # Create Tax Rate #
    ###################

    tax_rate = stripe.TaxRate.create(
        display_name="Sales Tax",
        description=zip_code, # set the description to the zip_code for easy querying
        percentage=percentage, # use the percentage we calculated. Stripe uses percentages, not decimals.
        inclusive=False, 
    )

Update Subscription
--------------------

Now that we have a Tax Rate in Stripe for this customer we just have to apply it to their subscription. 

.. code-block:: Python

    import stripe

    # You'll need to get your customer's subscription id for this part
    sub = stripe.Subscription.list(customer="{{Customer ID}}")[0]

    stripe_sub_data = stripe.Subscription.modify(
                sub.id, default_tax_rates=[tax_rate.id]
            )

🚀 And that's it! You're done. You can go into your Stripe dashboard and see that the invoice will now have a Sales Tax
line item. 

    