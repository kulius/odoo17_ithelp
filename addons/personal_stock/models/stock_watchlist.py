from odoo import models, fields, api
import twstock
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class StockWatchlist(models.Model):
    _name = 'stock.watchlist'
    _description = '股票觀察名單'

    name = fields.Char(string='名稱', required=True)
    stock_code = fields.Char(string='股票代碼', required=True)
    current_price = fields.Float(string='當前價格', digits=(10, 2))
    previous_close = fields.Float(string='前收盤價', digits=(10, 2))
    price_change = fields.Float(string='價格變動', digits=(10, 2))
    change_percentage = fields.Float(string='漲跌幅(%)', digits=(5, 2))
    last_update = fields.Datetime(string='最後更新時間')

    def update_stock_info(self):
        for record in self:
            try:
                stock_data = twstock.realtime.get(record.stock_code)
                if stock_data['success']:
                    record.current_price = float(stock_data['realtime']['latest_trade_price'])
                    if not record.previous_close:
                        record.previous_close = float(stock_data['realtime']['open'])
                    record.price_change = record.current_price - record.previous_close
                    record.change_percentage = (record.price_change / record.previous_close) * 100
                    record.last_update = datetime.now()
                else:
                    _logger.warning(f"無法獲取股票 {record.stock_code} 的數據")
            except Exception as e:
                _logger.error(f"更新股票 {record.stock_code} 資訊時發生錯誤: {str(e)}")

    @api.model
    def update_all_stocks(self):
        watchlists = self.search([])
        watchlists.update_stock_info()