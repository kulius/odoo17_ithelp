from odoo import models, fields, api

class StockKline(models.Model):
    _name = 'stock.kline'
    _description = '股票K線數據'

    watchlist_id = fields.Many2one('stock.watchlist', string='觀察名單', required=True)
    date = fields.Date('日期', required=True)
    open_price = fields.Float('開盤價', digits=(10, 2))
    close_price = fields.Float('收盤價', digits=(10, 2))
    high_price = fields.Float('最高價', digits=(10, 2))
    low_price = fields.Float('最低價', digits=(10, 2))
    volume = fields.Integer('成交量')

    _sql_constraints = [
        ('unique_watchlist_date', 'unique(watchlist_id, date)', '每個觀察名單的每個日期只能有一筆K線數據！')
    ]