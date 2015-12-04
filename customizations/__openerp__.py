{
    'name': "Customizations",

    'summary': """
        Customizations for test""",

    'description': """
        Customizations for test
    """,


    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'AGPL-3',
    'depends': [
		'base', 'account', 'sale', 'project', 'stock', 'mail', 'hr_timesheet_sheet', 
        'purchase', 'sale_stock', 'l10n_in', 'stock_account', 'web_debranding',
	],
    'data': [
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/stock_view.xml',
        'security/customizations_security.xml',
    ],
    'installable': True,
	'application': False,
	'auto_install': False,
}