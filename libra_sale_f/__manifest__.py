# Copyright 2023 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "libra_sale_f",
    "summary": "Mejoras solicitadas por el cliente",
    "version": "18.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/juanpgarza/libra-custom",
    "author": "juanpgarza",
    "license": "AGPL-3",
    "depends": [
            "sale",
            "sale_management",
            "stock",
            "product",
        ],
    "data": [
            'security/libra_sale_security.xml',
            'views/sale_order_views.xml',
            'data/libra_data.xml',
            'views/product_template_views.xml',            
        ],
    "installable": True,
}
