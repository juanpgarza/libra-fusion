# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Libra stock",
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
        "stock_voucher",
        "stock_ux",
        "sale",       
        ],
    "data": [
        'security/libra_security.xml',
        'views/stock_picking_views.xml',
        'views/report_stockpicking_operations.xml',
        'views/report_customer_delivery_views.xml',
        'security/ir.model.access.csv',
        'wizard/report_customer_delivery_wizard_views.xml',
        'views/sale_order_views.xml',
        'data/config_parameter.xml',
        'data/stock_data.xml',
        'views/stock_location_views.xml',
        'views/company.xml',
        'views/stock_quant_views.xml',
        ],
    "installable": True,
}
