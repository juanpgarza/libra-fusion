# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Libra Pronto",
    "summary": "",
    "version": "18.0.1.0.1",
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
            "sale_product_pack",
            "product",
            "sale_order_type",
            "payment_mode_st",
        ],
    "data": [
            'views/product_template_views.xml',
            'security/pronto_security.xml',
            'views/sale_order_views.xml',
            'views/stock_picking_views.xml',
            'views/report_stockpicking_operations.xml',            
            'views/purchase_order_views.xml',
            'views/stock_location_views.xml',
            'views/company.xml',
            'data/product_stock_data.xml',
            'views/res_partner_views.xml',
            'security/ir.model.access.csv',
            'views/report_customer_delivery_views.xml',            
            'wizard/report_customer_delivery_wizard_views.xml'
        ],
    "installable": True,
}
