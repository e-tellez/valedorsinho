"""Merchant vertical definitions and their suggested /payments payloads.

Each vertical has:
- key: unique identifier used by POST /api/tools/payload-suggested
- label: display name shown in the UI
- description: short explanation shown in the UI
- payload: full recommended /payments request body sourced from the
  Adyen risk-fields Postman collection

Shared building-blocks (_prefixed) keep the payload definitions DRY.
All values are representative test/sample data — never real credentials.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Shared payload building blocks
# ---------------------------------------------------------------------------

_PAYMENT_METHOD: dict[str, Any] = {
    "type": "scheme",
    "encryptedCardNumber": "test_4111111111111111",
    "encryptedExpiryMonth": "test_03",
    "encryptedExpiryYear": "test_2030",
    "encryptedSecurityCode": "test_737",
    "holderName": "Test Name",
}

_BROWSER_INFO: dict[str, Any] = {
    "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "colorDepth": 24,
    "javaEnabled": True,
    "language": "en-GB",
    "screenHeight": 823,
    "screenWidth": 1535,
    "timeZoneOffset": "-120",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

_BILLING_ADDRESS_NL: dict[str, Any] = {
    "city": "Amsterdam",
    "country": "NL",
    "houseNumberOrName": "124",
    "postalCode": "90210",
    "street": "Rokin Street",
}

_BILLING_ADDRESS_MX: dict[str, Any] = {
    "city": "CDMX",
    "country": "MX",
    "houseNumberOrName": "124",
    "postalCode": "90210",
    "street": "Rokin Street",
}

_DELIVERY_ADDRESS_NL: dict[str, Any] = {
    "city": "Amsterdam",
    "country": "NL",
    "houseNumberOrName": "124",
    "postalCode": "90210",
    "street": "Rokin Street",
}

_RISK_DATA: dict[str, Any] = {"clientData": "fdf9sd09f8sdsdfsd9f7sd9f"}

# ---------------------------------------------------------------------------
# Vertical definitions
# ---------------------------------------------------------------------------

VERTICALS: list[dict[str, Any]] = [
    # -------------------------------------------------------------------
    # 1. Minimum Mandatory
    # -------------------------------------------------------------------
    {
        "key": "minimum_mandatory",
        "label": "Minimum Mandatory",
        "description": "Core risk fields recommended for every /payments request.",
        "payload": {
            "amount": {"currency": "MXN", "value": 10000},
            "reference": "RISK-FIELDS-MINIMUM-001",
            "paymentMethod": _PAYMENT_METHOD,
            "shopperInteraction": "Ecommerce",
            "recurringProcessingModel": "CardOnFile",
            "returnUrl": "https://your-company.com/checkout/result",
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "shopperReference": "SHOPPER_UNIQUE_REFERENCE",
            "shopperName": {"firstName": "John", "lastName": "Doe"},
            "shopperEmail": "support@adyen.com",
            "shopperIP": "127.0.0.1",
            "telephoneNumber": "+6140337086",
            "deviceFingerprint": "98D9FSDOIUFW",
            "billingAddress": _BILLING_ADDRESS_NL,
            "deliveryAddress": _DELIVERY_ADDRESS_NL,
            "browserInfo": _BROWSER_INFO,
            "riskData": _RISK_DATA,
        },
    },
    # -------------------------------------------------------------------
    # 2. Hotels
    # -------------------------------------------------------------------
    {
        "key": "hotels",
        "label": "Hotels",
        "description": "Accommodation and hospitality bookings.",
        "payload": {
            "amount": {"currency": "MXN", "value": 10000},
            "reference": "RISK-FIELDS-HOTELS-001",
            "paymentMethod": _PAYMENT_METHOD,
            "shopperInteraction": "Ecommerce",
            "recurringProcessingModel": "CardOnFile",
            "returnUrl": "https://your-company.com/checkout/result",
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "shopperReference": "SHOPPER_UNIQUE_REFERENCE",
            "shopperName": {"firstName": "John", "lastName": "Doe"},
            "shopperEmail": "support@adyen.com",
            "shopperIP": "127.0.0.1",
            "telephoneNumber": "+06140337086",
            "deviceFingerprint": "98D9FSDOIUFW",
            "billingAddress": _BILLING_ADDRESS_MX,
            "deliveryAddress": _DELIVERY_ADDRESS_NL,
            "browserInfo": _BROWSER_INFO,
            "riskData": _RISK_DATA,
            "deliverAt": "2017-07-17T13:42:40.428+01:00",
            "additionalData": {
                "lodging.checkInDate": "20260422",
                "lodging.checkOutDate": "20260522",
                "lodging.room1.numberOfNights": "5",
                "riskdata.travellingCustomerName": True,
                "riskdata.hotelName": "Oaks on William",
                "riskdata.hotelCountry": "AU",
                "riskdata.hotelCity": "Melbourne",
                "riskdata.hotelRoomType": "One Bedroom Apartment - 1 Queen bed",
                "riskdata.hotelGuestNumber": 2,
                "riskdata.hotelGuestFirstName": "Raymond",
                "riskdata.hotelGuestLastName": "Shelley",
                "riskdata.hotelCancellationPolicy": "Non refundable",
                "riskdata.emergencyBooking": False,
            },
        },
    },
    # -------------------------------------------------------------------
    # 3. Airlines
    # -------------------------------------------------------------------
    {
        "key": "airlines",
        "label": "Airlines",
        "description": "Flight bookings and air travel payments.",
        "payload": {
            "amount": {"currency": "MXN", "value": 10000},
            "reference": "RISK-FIELDS-AIRLINES-001",
            "paymentMethod": _PAYMENT_METHOD,
            "shopperInteraction": "Ecommerce",
            "recurringProcessingModel": "CardOnFile",
            "returnUrl": "https://your-company.com/checkout/result",
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "shopperReference": "SHOPPER_UNIQUE_REFERENCE",
            "shopperName": {"firstName": "John", "lastName": "Doe"},
            "shopperEmail": "support@adyen.com",
            "shopperIP": "127.0.0.1",
            "telephoneNumber": "+06140337086",
            "deviceFingerprint": "98D9FSDOIUFW",
            "billingAddress": _BILLING_ADDRESS_MX,
            "deliveryAddress": _DELIVERY_ADDRESS_NL,
            "browserInfo": _BROWSER_INFO,
            "riskData": _RISK_DATA,
            "additionalData": {
                "airline.passenger_name": "Mr John",
                "airline.airline_code": "074",
                "airline.passenger1.first_name": "John",
                "airline.passenger1.last_name": "Doe",
                "airline.passenger1.traveller_type": "ADT",
                "airline.passenger1.date_of_birth": "1996-04-19",
                "airline.passenger1.phone_number": "525617687955",
                "airline.leg1.depart_airport": "SGP",
                "airline.leg1.destination_code": "AMS",
                "airline.leg1.flight_number": "KL114",
                "airline.leg1.carrier_code": "KL",
                "airline.leg1.class_of_travel": "F",
                "airline.leg1.stop_over_code": "O",
                "airline.leg1.date_of_travel": "2030-03-22 11:00",
                "airline.leg1.depart_tax": "100",
                "airline.leg1.fare_base_code": "F",
                "airline.leg2.depart_airport": "CDG",
                "airline.leg2.destination_code": "FRA",
                "airline.leg2.flight_number": "4321",
                "airline.leg2.carrier_code": "AF",
                "airline.leg2.class_of_travel": "Y",
                "airline.leg2.stop_over_code": "X",
                "airline.leg2.date_of_travel": "2030-03-22 11:00",
                "airline.leg2.depart_tax": "100",
                "airline.leg2.fare_base_code": "Y",
                "riskdata.deliveryDate": "2030-10-24",
                "riskdata.firstDepartureCountry": "SGP",
                "riskdata.finalDestinationCountry": "FRA",
                "riskdata.hoursToDelivery": 24,
                "riskdata.passengerNameIsCardholderName": True,
            },
        },
    },
    # -------------------------------------------------------------------
    # 4. Digital Wallet
    # -------------------------------------------------------------------
    {
        "key": "digital_wallet",
        "label": "Digital Wallet",
        "description": "Digital wallet and stored-value payment flows.",
        "payload": {
            "amount": {"currency": "MXN", "value": 10000},
            "reference": "RISK-FIELDS-DIGITAL-WALLET-001",
            "paymentMethod": _PAYMENT_METHOD,
            "shopperInteraction": "Ecommerce",
            "recurringProcessingModel": "CardOnFile",
            "returnUrl": "https://your-company.com/checkout/result",
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "shopperReference": "SHOPPER_UNIQUE_REFERENCE",
            "shopperName": {"firstName": "John", "lastName": "Doe"},
            "shopperEmail": "support@adyen.com",
            "shopperIP": "127.0.0.1",
            "telephoneNumber": "+6140337086",
            "deviceFingerprint": "98D9FSDOIUFW",
            "deliverAt": "2017-07-17T13:42:40.428+01:00",
            "billingAddress": _BILLING_ADDRESS_NL,
            "deliveryAddress": _DELIVERY_ADDRESS_NL,
            "browserInfo": _BROWSER_INFO,
            "riskData": _RISK_DATA,
            "additionalData": {
                "riskdata.daysSinceDeviceChanged": 30,
                "riskdata.daysSinceEmailChanged": 30,
                "riskdata.daysSincePasswordChanged": 30,
                "riskdata.daysSinceShopperAccountCreation": 30,
                "riskdata.externalDeviceFingerprint": "asjkpa4809qwie123568307190u3alskhda43lksd",
                "riskdata.numberOfPasswordChanges": 1,
                "riskdata.userVerificationMethod": "Passport",
                "riskdata.walletType": "Basic",
            },
        },
    },
    # -------------------------------------------------------------------
    # 5. Subscription
    # -------------------------------------------------------------------
    {
        "key": "subscription",
        "label": "Subscription",
        "description": "Recurring billing and subscription-based services.",
        "payload": {
            "amount": {"currency": "MXN", "value": 10000},
            "reference": "RISK-FIELDS-SUBSCRIPTION-001",
            "paymentMethod": _PAYMENT_METHOD,
            "shopperInteraction": "Ecommerce",
            "recurringProcessingModel": "CardOnFile",
            "returnUrl": "https://your-company.com/checkout/result",
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "shopperReference": "SHOPPER_UNIQUE_REFERENCE",
            "shopperName": {"firstName": "John", "lastName": "Doe"},
            "shopperEmail": "support@adyen.com",
            "shopperIP": "127.0.0.1",
            "telephoneNumber": "+6140337086",
            "deviceFingerprint": "98D9FSDOIUFW",
            "deliverAt": "2017-07-17T13:42:40.428+01:00",
            "billingAddress": _BILLING_ADDRESS_NL,
            "deliveryAddress": _DELIVERY_ADDRESS_NL,
            "browserInfo": _BROWSER_INFO,
            "riskData": _RISK_DATA,
            "additionalData": {
                "riskdata.daysSinceDeviceChanged": 30,
                "riskdata.daysSinceEmailChanged": 30,
                "riskdata.daysSincePasswordChanged": 30,
                "riskdata.daysSinceShopperAccountCreation": 30,
                "riskdata.externalDeviceFingerprint": "asjkpa4809qwie123568307190u3alskhda43lksd",
                "riskdata.IMEINumber": 348920910128,
                "riskdata.numberOfPasswordChanges": 1,
                "riskdata.membershipType": "Passport",
                "riskdata.walletUsernameType": "Basic",
            },
        },
    },
    # -------------------------------------------------------------------
    # 6. Ride-Hailing
    # -------------------------------------------------------------------
    {
        "key": "ride_hailing",
        "label": "Ride-Hailing",
        "description": "Ride-hailing, car-sharing, and on-demand transportation.",
        "payload": {
            "amount": {"currency": "MXN", "value": 10000},
            "reference": "RISK-FIELDS-RIDE-HAILING-001",
            "paymentMethod": _PAYMENT_METHOD,
            "shopperInteraction": "Ecommerce",
            "recurringProcessingModel": "CardOnFile",
            "returnUrl": "https://your-company.com/checkout/result",
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "shopperReference": "SHOPPER_UNIQUE_REFERENCE",
            "shopperName": {"firstName": "John", "lastName": "Doe"},
            "shopperEmail": "support@adyen.com",
            "shopperIP": "127.0.0.1",
            "telephoneNumber": "+6140337086",
            "deviceFingerprint": "98D9FSDOIUFW",
            "deliverAt": "2017-07-17T13:42:40.428+01:00",
            "billingAddress": _BILLING_ADDRESS_NL,
            "deliveryAddress": _DELIVERY_ADDRESS_NL,
            "browserInfo": _BROWSER_INFO,
            "riskData": _RISK_DATA,
            "additionalData": {
                "riskdata.countOfPreviousRides": 10,
                "riskdata.countOfPreviousRidesWithSameDriver": 10,
                "riskdata.daysSinceDeviceChanged": 30,
                "riskdata.daysSinceEmailChanged": 30,
                "riskdata.daysSincePasswordChanged": 30,
                "riskdata.daysSinceShopperAccountWasCreated": 10,
                "riskdata.destinationLatitude": "-31.7427433488299",
                "riskdata.destinationLongitude": "115.767943451775",
                "riskdata.deviceLanguage": "English",
                "riskdata.distanceBetweenDriverRider": 5,
                "riskdata.failedLoginCount": 5,
                "riskdata.gpsDisabled": True,
                "riskdata.IMEINumber": 348920910128,
                "riskdata.IMSI": "112233445566778",
                "riskdata.isItVoip": True,
                "riskdata.jailBrokenDevice": True,
                "riskdata.latestAppVersion": True,
                "riskdata.numberOfPasswordChanges": 1,
                "riskdata.originLatitude": "-31.6668748",
                "riskdata.originLongitude": "115.7032165",
                "riskdata.operatingSystem": "iOS",
                "riskdata.OSVersion": "iOS 14",
                "riskdata.rideCity": "Perth",
                "riskdata.rideState": "WA",
                "riskdata.userLatitude": "-31.6668883",
                "riskdata.userLongitude": "115.7031934",
            },
        },
    },
    # -------------------------------------------------------------------
    # 7. Restaurants
    # -------------------------------------------------------------------
    {
        "key": "restaurants",
        "label": "Restaurants",
        "description": "Food and beverage, quick-service, and delivery orders.",
        "payload": {
            "amount": {"currency": "MXN", "value": 10000},
            "reference": "RISK-FIELDS-RESTAURANTS-001",
            "paymentMethod": _PAYMENT_METHOD,
            "shopperInteraction": "Ecommerce",
            "recurringProcessingModel": "CardOnFile",
            "returnUrl": "https://your-company.com/checkout/result",
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "shopperReference": "SHOPPER_UNIQUE_REFERENCE",
            "shopperName": {"firstName": "John", "lastName": "Doe"},
            "shopperEmail": "support@adyen.com",
            "shopperIP": "127.0.0.1",
            "telephoneNumber": "+6140337086",
            "deviceFingerprint": "98D9FSDOIUFW",
            "deliverAt": "2017-07-17T13:42:40.428+01:00",
            "billingAddress": _BILLING_ADDRESS_NL,
            "deliveryAddress": _DELIVERY_ADDRESS_NL,
            "browserInfo": _BROWSER_INFO,
            "riskData": _RISK_DATA,
            "additionalData": {
                "riskdata.basket.item1.amountPerItem": "20000",
                "riskdata.basket.item1.itemID": "KB681",
                "riskdata.basket.item1.productTitle": "Krabby Patty",
                "riskdata.basket.item1.category": "Famous Burgers",
                "riskdata.basket.item1.currency": "MXN",
                "riskdata.basket.item1.quantity": "3",
                "riskdata.guestCheckOut": True,
                "riskdata.orderType": "Delivery",
                "riskdata.storeCity": "Melbourne",
                "riskdata.storeState": "VIC",
                "riskdata.storeCountry": "AU",
                "riskdata.storeID": "30037",
                "riskdata.storeType": "Franchisee",
            },
        },
    },
    # -------------------------------------------------------------------
    # 8. Retail
    # -------------------------------------------------------------------
    {
        "key": "retail",
        "label": "Retail",
        "description": "E-commerce and in-store retail transactions.",
        "payload": {
            "amount": {"currency": "MXN", "value": 10000},
            "reference": "ORDER-001",
            "paymentMethod": _PAYMENT_METHOD,
            "shopperInteraction": "Ecommerce",
            "recurringProcessingModel": "CardOnFile",
            "returnUrl": "https://your-company.com/checkout/result",
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "shopperReference": "SHOPPER_UNIQUE_REFERENCE",
            "shopperName": {"firstName": "John", "lastName": "Doe"},
            "shopperEmail": "support@adyen.com",
            "shopperIP": "127.0.0.1",
            "telephoneNumber": "+06140337086",
            "deviceFingerprint": "98D9FSDOIUFW",
            "billingAddress": _BILLING_ADDRESS_MX,
            "deliveryAddress": _DELIVERY_ADDRESS_NL,
            "browserInfo": _BROWSER_INFO,
            "riskData": _RISK_DATA,
            "additionalData": {
                "riskdata.basket.item1.amountPerItem": "20000",
                "riskdata.basket.item1.brand": "Minisoo",
                "riskdata.basket.item1.category": "Skincare",
                "riskdata.basket.item1.currency": "MXN",
                "riskdata.basket.item1.itemID": "CAT681",
                "riskdata.basket.item1.productTitle": "DayWear Multi-Protection Sunscreen",
                "riskdata.basket.item1.quantity": "3",
                "riskdata.basket.item1.sku": "FJFSO22",
                "riskdata.basket.item1.size": "50ml",
                "riskdata.basket.item1.upc": "27131763512",
                "riskdata.daysSinceDeliveryAddressChanged": "90",
                "riskdata.daysSinceDeviceChanged": "90",
                "riskdata.daysSinceEmailChanged": "90",
                "riskdata.daysSincePasswordChanged": "90",
                "riskdata.daysSincePhoneNumberChanged": "90",
                "riskdata.daysSinceShopperAccountWasCreated": "100",
                "riskData.deliveryMethod": "Express",
                "riskdata.failedLoginCount": "5",
                "riskdata.giftCard": False,
                "riskdata.giftMessage": False,
                "riskdata.giftWrap": False,
                "riskdata.guestCheckOut": False,
                "riskdata.numberOfPasswordChanges": "3",
                "riskdata.promotion": False,
                "riskdata.promotionCode": "FIRSTTIMEOFF20",
                "riskdata.timeFromBasketToCheckout": "30",
                "riskdata.timeToDelivery": "3",
            },
        },
    },
    # -------------------------------------------------------------------
    # 9. Tickets
    # -------------------------------------------------------------------
    {
        "key": "tickets",
        "label": "Tickets",
        "description": "Event, concert, and entertainment ticket sales.",
        "payload": {
            "amount": {"currency": "MXN", "value": 10000},
            "reference": "RISK-FIELDS-TICKETS-001",
            "paymentMethod": _PAYMENT_METHOD,
            "shopperInteraction": "Ecommerce",
            "recurringProcessingModel": "CardOnFile",
            "returnUrl": "https://your-company.com/checkout/result",
            "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
            "shopperReference": "SHOPPER_UNIQUE_REFERENCE",
            "shopperName": {"firstName": "John", "lastName": "Doe"},
            "shopperEmail": "support@adyen.com",
            "shopperIP": "127.0.0.1",
            "telephoneNumber": "+06140337086",
            "deviceFingerprint": "98D9FSDOIUFW",
            "deliverAt": "2030-07-17T13:42:40.428+01:00",
            "billingAddress": _BILLING_ADDRESS_MX,
            "deliveryAddress": _DELIVERY_ADDRESS_NL,
            "browserInfo": _BROWSER_INFO,
            "riskData": _RISK_DATA,
            "additionalData": {
                "riskdata.basket.item1.amountPerItem": "20000",
                "riskdata.basket.item1.category": "Rock/Metal",
                "riskdata.basket.item1.currency": "MXN",
                "riskdata.basket.item1.itemID": "CAT681",
                "riskdata.basket.item1.productTitle": "The Beatles",
                "riskdata.basket.item1.quantity": "3",
                "riskdata.basket.item1.sku": "FJFSO22",
                "riskdata.daysSinceDeviceChanged": "90",
                "riskdata.daysSinceEmailChanged": "90",
                "riskdata.daysSincePasswordChanged": "90",
                "riskdata.daysSincePhoneNumberChanged": "90",
                "riskdata.daysSinceShopperAccountWasCreated": "100",
                "riskData.deliveryMethod": "Express",
                "riskdata.failedLoginCount": "5",
                "riskdata.giftCard": False,
                "riskdata.giftMessage": False,
                "riskdata.guestCheckOut": False,
                "riskdata.numberOfPasswordChanges": "3",
                "riskdata.promotion": False,
                "riskdata.promotionCode": "FIRSTTIMEOFF20",
                "riskdata.timeFromBasketToCheckout": "30",
                "riskdata.timeToDelivery": "3",
            },
        },
    },
]
