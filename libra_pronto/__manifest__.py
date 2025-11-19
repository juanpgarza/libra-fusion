# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Libra Pronto",
    "summary": "",
    "version": "18.0.1.0.0",
    "category": "",
    "website": "https://github.com/juanpgarza/libra-fusion",
    "author": "juanpgarza",
    "license": "AGPL-3",
    "depends": [
        # CORE ce
        #         
            "sale",
            "sale_margin",
            "stock",
        ],
    "data": [
            'views/product_template_views.xml',
            'security/pronto_security.xml',
            'views/sale_order_views.xml',
            'views/stock_picking_views.xml',
            'views/report_stockpicking_operations.xml',            
        ],
    "installable": True,
}
