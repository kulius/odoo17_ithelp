from odoo import models, fields, api

class Watchlist(models.Model):
    _name = 'stock.watchlist'
    _description = '股票觀察名單'

    name = fields.Char('名稱', required=True)
    stock_code = fields.Char('股票代號', required=True)

