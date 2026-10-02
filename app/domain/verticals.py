"""Merchant vertical definitions and their suggested /payments payloads.

Each vertical has:
- key: unique identifier
- label: display name
- description: short explanation shown in the UI
- payload: recommended /payments request fields
"""

from __future__ import annotations

from typing import Any

VERTICALS: list[dict[str, Any]] = [
    {
        "key": "minimum_mandatory",
        "label": "Minimum Mandatory",
        "description": "Core risk fields recommended for every /payments request.",
        "payload": {
            "shopperIP": "192.0.2.1",
            "channel": "Web",
            "origin": "https://your-website.com",
            "countryCode": "NL",
            "shopperLocale": "en-US",
            "browserInfo": {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
                "acceptHeader": "*/*",
                "language": "en-US",
                "colorDepth": 24,
                "screenHeight": 1080,
                "screenWidth": 1920,
                "timeZoneOffset": -60,
                "javaEnabled": False,
            },
        },
    },
    {
        "key": "hotels",
        "label": "Hotels",
        "description": "Lodging-specific fields for hotel bookings.",
        "payload": {
            "additionalData": {
                "lodging.checkInDate": "2024-01-15",
                "lodging.checkOutDate": "2024-01-18",
                "lodging.totalRoomTax": "1500",
                "lodging.roomTax": "500",
                "lodging.roomRate": "5000",
                "lodging.noShowIndicator": "0",
                "lodging.folioNumber": "FOL-001",
                "lodging.fireSafetyActIndicator": "1",
                "lodging.propertyPhoneNumber": "+1-800-000-0000",
            }
        },
    },
    {
        "key": "airlines",
        "label": "Airlines",
        "description": "Airline-specific fields for flight bookings.",
        "payload": {
            "additionalData": {
                "airline.flight_date": "2024-01-15",
                "airline.flight_number": "AB1234",
                "airline.passenger_name": "John Doe",
                "airline.ticket_number": "ABC123456789",
                "airline.origin_airport_code": "MEX",
                "airline.destination_airport_code": "JFK",
                "airline.airline_code": "AB",
                "airline.number_in_party": "1",
                "airline.agency_plan_name": "DIRECT",
                "airline.boarding_fee": "0",
            }
        },
    },
    {
        "key": "digital_wallet",
        "label": "Digital Wallet",
        "description": "E-wallet and top-up flows.",
        "payload": {
            "shopperReference": "YOUR_SHOPPER_REFERENCE",
            "shopperEmail": "shopper@example.com",
            "shopperInteraction": "Ecommerce",
        },
    },
    {
        "key": "subscription",
        "label": "Subscription",
        "description": "Recurring billing and subscription payments.",
        "payload": {
            "shopperReference": "YOUR_SHOPPER_REFERENCE",
            "shopperEmail": "shopper@example.com",
            "storePaymentMethod": True,
            "shopperInteraction": "Ecommerce",
            "recurringProcessingModel": "Subscription",
        },
    },
    {
        "key": "ride_hailing",
        "label": "Ride Hailing",
        "description": "Taxi and ride-sharing payments.",
        "payload": {
            "additionalData": {
                "ridehailing.arrivalCity": "Amsterdam",
                "ridehailing.departureCity": "Rotterdam",
                "ridehailing.driverName": "Jane Doe",
                "ridehailing.vehicleType": "sedan",
                "ridehailing.pickupDate": "2024-01-15T10:00:00.000Z",
                "ridehailing.dropoffDate": "2024-01-15T10:45:00.000Z",
            }
        },
    },
    {
        "key": "restaurants",
        "label": "Restaurants",
        "description": "Food & beverage point-of-sale.",
        "payload": {
            "additionalData": {
                "foodAndBeverage.customerRefNumber": "ORDER-001",
                "foodAndBeverage.tipAmount": "200",
            }
        },
    },
    {
        "key": "retail",
        "label": "Retail",
        "description": "Physical retail and ECOM.",
        "payload": {
            "shopperReference": "YOUR_SHOPPER_REFERENCE",
            "shopperEmail": "shopper@example.com",
            "shopperInteraction": "Ecommerce",
        },
    },
    {
        "key": "tickets",
        "label": "Tickets",
        "description": "Event ticketing and admission.",
        "payload": {
            "additionalData": {
                "ticket.number_in_party": "2",
                "ticket.event_city": "Amsterdam",
                "ticket.event_date": "2024-03-15T20:00:00.000Z",
                "ticket.event_name": "Concert",
                "ticket.venue_name": "Ziggo Dome",
            }
        },
    },
]
