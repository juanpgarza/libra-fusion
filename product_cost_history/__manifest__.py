{
    'name': 'Historial de Costo de Reposición',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Automatiza y registra el historial de cambios en el costo de reposición.',
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/cost_history_views.xml',        
    ],
    "author": "juanpgarza",
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}