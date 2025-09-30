# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Libra base",
    "summary": "",
    "version": "18.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/juanpgarza/libra-custom",
    "author": "juanpgarza",
    "license": "AGPL-3",
    "depends": [
        # CORE ce
        "stock",
        "stock_picking_invoice_link", # OCA
        "sale_order_type", # OCA        
        ],
    "data": [
        'security/libra_security.xml',
        'views/res_partner_views.xml',
        ],
    "installable": True,
}
