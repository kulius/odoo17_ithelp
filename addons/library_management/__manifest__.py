{
    'name': 'Library Management',
    'version': '17.0',
    'depends': ['base', 'mail'],
    'data': [
        'views/library_book_views.xml',
        'views/library_student_views.xml',
        'views/library_book_category_views.xml',
        'views/library_management_menu.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}