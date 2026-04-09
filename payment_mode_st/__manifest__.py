# Copyright 2025 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Payment Mode",
    "summary": "",
    "version": "18.0.1.0.0",
    "category": "Misc",
    "website": "",
    "author": "juanpgarza",
    "license": "AGPL-3",
    "depends": [
            "base",
            "sale",
            "account",
            ],
    "data": [
        'security/ir.model.access.csv',        
        'views/payment_mode_st_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        ],
    "installable": True,
}
