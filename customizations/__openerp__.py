{
    'name': "dvd",

    'summary': """
        Customizations for test""",

    'description': """
        Customizations for test
    """,


    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'AGPL-3',
    'depends': [
		'base', 'account', 'sale', 'project', 'stock', 'mail', 'hr_timesheet_sheet', 'purchase',
	],
    'data': [
        'views/module_name_view.xml',
    ],
    'installable': True,
	'application': False,
	'auto_install': False,
}