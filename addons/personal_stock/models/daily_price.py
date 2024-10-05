from odoo import models, fields

class DailyPrice(models.Model):
    _name = 'stock.daily.price'
    _description = '每日股價'

    stock_id = fields.Many2one('stock.stock', string='股票', required=True)
    date = fields.Date('日期', required=True)
    open_price = fields.Float('開盤價', digits=(10, 2))
    close_price = fields.Float('收盤價', digits=(10, 2))
    high_price = fields.Float('最高價', digits=(10, 2))
    low_price = fields.Float('最低價', digits=(10, 2))
    volume = fields.Integer('成交量')

    _sql_constraints = [
        ('unique_stock_date', 'unique(stock_id, date)', '每支股票每天只能有一筆價格記錄！')
    ]