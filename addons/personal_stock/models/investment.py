from odoo import models, fields, api

class Investment(models.Model):
    _name = 'stock.investment'
    _description = '投資記錄'

    stock_id = fields.Many2one('stock.stock', string='股票', required=True)
    date = fields.Date('購買日期', required=True)
    price = fields.Float('購買價格', digits=(10, 2), required=True)
    quantity = fields.Integer('購買數量', required=True)

    @api.depends('price', 'quantity', 'stock_id.current_price')
    def _compute_profit_loss(self):
        for investment in self:
            current_value = investment.stock_id.current_price * investment.quantity
            cost = investment.price * investment.quantity
            investment.profit_loss = current_value - cost

    profit_loss = fields.Float('損益', compute='_compute_profit_loss', store=True)