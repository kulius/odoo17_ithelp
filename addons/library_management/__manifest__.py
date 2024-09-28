{
    'name': 'Library Management',
    'version': '17.0',
    'depends': ['base', 'mail'],
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',

        'views/library_book_loan_views.xml',
        'views/library_book_views.xml',
        'views/library_student_views.xml',
        'views/library_book_category_views.xml',

        'views/res_users_views.xml',

        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',

        'views/library_management_menu.xml',

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}