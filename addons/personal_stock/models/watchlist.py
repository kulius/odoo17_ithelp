from odoo import models, fields, api
import twstock
from datetime import datetime, timedelta
import logging
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import io
import base64

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
    kline_ids = fields.One2many('stock.kline', 'watchlist_id', string='K線數據')

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

    def update_kline_data(self):
        for record in self:
            try:
                stock = twstock.Stock(record.stock_code)
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=365)

                # 獲取近一年的數據
                kline_data = stock.fetch_from(start_date.year, start_date.month)

                for data in kline_data:
                    if start_date <= data.date.date() <= end_date:
                        kline = self.env['stock.kline'].search([
                            ('watchlist_id', '=', record.id),
                            ('date', '=', data.date.date())
                        ])
                        kline_values = {
                            'open_price': data.open,
                            'close_price': data.close,
                            'high_price': data.high,
                            'low_price': data.low,
                            'volume': data.capacity
                        }
                        if kline:
                            kline.write(kline_values)
                        else:
                            kline_values.update({
                                'watchlist_id': record.id,
                                'date': data.date.date(),
                            })
                            self.env['stock.kline'].create(kline_values)

                record.last_update = datetime.now()
                _logger.info(f"成功更新股票 {record.stock_code} 的K線數據")
            except Exception as e:
                _logger.error(f"更新股票 {record.stock_code} K線數據時發生錯誤: {str(e)}")

    def show_kline_chart(self):
        self.ensure_one()
        kline_data = self.kline_ids.sorted(key=lambda r: r.date)

        # 將數據轉換為 pandas DataFrame
        df = pd.DataFrame({
            'Date': pd.to_datetime(kline_data.mapped('date')),
            'Open': kline_data.mapped('open_price'),
            'High': kline_data.mapped('high_price'),
            'Low': kline_data.mapped('low_price'),
            'Close': kline_data.mapped('close_price'),
            'Volume': kline_data.mapped('volume')
        })
        df.set_index('Date', inplace=True)

        # 確保索引是 DatetimeIndex 類型
        df.index = pd.to_datetime(df.index)

        # 設置 K 線圖樣式
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc)

        # 創建一個 BytesIO 對象來保存圖片
        buf = io.BytesIO()

        # 繪製 K 線圖
        mpf.plot(df, type='candle', style=s, title=f'{self.name} ({self.stock_code}) K線圖',
                 volume=True, figsize=(10, 8), savefig=dict(fname=buf, format='png'))

        # 將圖片保存為附件
        buf.seek(0)
        attachment = self.env['ir.attachment'].create({
            'name': f'{self.name}_{self.stock_code}_kline_chart.png',
            'datas': base64.b64encode(buf.getvalue()),
            'res_model': self._name,
            'res_id': self.id,
        })

        # 返回一個動作來顯示附件
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    # 保留其他方法的定義