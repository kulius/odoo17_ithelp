from odoo import models, fields, api

class StockWatchlistAdvice(models.Model):
    _name = 'stock.watchlist.advice'
    _description = '股票觀察名單建議'

    watchlist_id = fields.Many2one('stock.watchlist', string='觀察名單', required=True)
    date = fields.Date('建議日期', required=True, default=fields.Date.today)
    advice_type = fields.Selection([('buy', '買入'), ('sell', '賣出'), ('hold', '持有')], string='建議類型', required=True)
    reason = fields.Text('建議理由')
    target_price = fields.Float('目標價格', digits=(10, 2))
    confidence = fields.Selection([('low', '低'), ('medium', '中'), ('high', '高')], string='信心程度')

    _sql_constraints = [
        ('unique_watchlist_date', 'unique(watchlist_id, date)', '每個觀察名單每天只能有一個建議！')
    ]