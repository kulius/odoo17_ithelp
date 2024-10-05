from odoo import models, fields, api

class Stock(models.Model):
    _name = 'stock.stock'
    _description = '股票'

    name = fields.Char('股票名稱', required=True)
    code = fields.Char('股票代號', required=True)
    current_price = fields.Float('當前價格', digits=(10, 2))
    last_update = fields.Datetime('最後更新時間')

    investment_ids = fields.One2many('stock.investment', 'stock_id', string='投資記錄')
    daily_price_ids = fields.One2many('stock.daily.price', 'stock_id', string='每日價格')

    @api.depends('investment_ids', 'current_price')
    def _compute_total_value(self):
        for stock in self:
            total_quantity = sum(inv.quantity for inv in stock.investment_ids)
            stock.total_value = total_quantity * stock.current_price

    total_value = fields.Float('總價值', compute='_compute_total_value', store=True)