# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Libra account f",
    "summary": "",
    "version": "18.0.1.0.0",
    "category": "account",
    "website": "https://github.com/juanpgarza/libra-fusion",
    "author": "juanpgarza",
    "license": "AGPL-3",
    "depends": [
        # CORE ce
        "account",       
        ],
    "data": [
        'security/libra_security.xml',
        'views/account_payment_views.xml',

        ],
    "installable": True,
}
