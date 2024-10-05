from odoo import models, fields

class Advice(models.Model):
    _name = 'stock.advice'
    _description = '投資建議'

    stock_id = fields.Many2one('stock.stock', string='股票', required=True)
    date = fields.Date('建議日期', required=True)
    type = fields.Selection([('buy', '買入'), ('sell', '賣出')], string='建議類型', required=True)
    reason = fields.Text('建議理由')
    target_price = fields.Float('目標價格', digits=(10, 2))