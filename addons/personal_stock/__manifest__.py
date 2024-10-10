{
    'name': '個人投資管理系統',
    'version': '1.0',
    'category': 'Finance',
    'summary': '管理個人股票投資、記錄每日漲跌情況、提供購買及賣出建議',
    'description': """
個人投資管理系統
================
這是一個針對 Odoo 17 開發的個人投資管理系統 Addons，目標是協助個人管理股票投資、記錄每日漲跌情況、並提供購買及賣出建議。

主要功能：
- 個人股票投資管理
- 個人股票每日漲跌記錄
- 所有股票的漲跌情況總覽
- 購買及賣出股票的建議
- 自定義股票觀察名單
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_views.xml',
        'views/investment_views.xml',
        'views/daily_price_views.xml',
        'views/advice_views.xml',
        'views/watchlist_views.xml',
        'views/menu.xml',
        'data/demo_data.xml',
        'data/cron_jobs.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['mplfinance', 'matplotlib', 'pandas'],
    },
}