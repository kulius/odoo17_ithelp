from operator import truediv

from odoo import models, fields, api
import twstock
from datetime import datetime, timedelta
import logging
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import io
import base64
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

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
    advice_ids = fields.One2many('stock.watchlist.advice', 'watchlist_id', string='投資建議')
    prediction = fields.Selection([('up', '上漲'), ('down', '下跌')], string='預測結果')
    prediction_confidence = fields.Float(string='預測置信度', digits=(5, 2))

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

    def generate_advice(self):
        self.ensure_one()
        today = fields.Date.today()- timedelta(days=1)

        # 獲取最近30天的K線數據
        kline_data = self.env['stock.kline'].search([
            ('watchlist_id', '=', self.id),
            ('date', '>=', today - timedelta(days=60)),
            ('date', '<=', today)
        ], order='date asc')

        if len(kline_data) < 30:
            return  # 數據不足，無法生成建議

        # 計算技術指標
        close_prices = np.array(kline_data.mapped('close_price'))
        sma5 = np.mean(close_prices[-5:])
        sma20 = np.mean(close_prices[-20:])
        rsi = self._calculate_rsi(close_prices)

        # 生成建議
        advice_type = 'hold'
        reason = []
        confidence = 'medium'

        if close_prices[-1] > sma5 and sma5 > sma20:
            advice_type = 'buy'
            reason.append('價格突破5日和20日均線')
            confidence = 'high'
        elif close_prices[-1] < sma5 and sma5 < sma20:
            advice_type = 'sell'
            reason.append('價格跌破5日和20日均線')
            confidence = 'high'

        if rsi > 70:
            advice_type = 'sell'
            reason.append('RSI超買（{}）'.format(round(rsi, 2)))
        elif rsi < 30:
            advice_type = 'buy'
            reason.append('RSI超賣（{}）'.format(round(rsi, 2)))

        # 創建或更新建議
        advice = self.env['stock.watchlist.advice'].search([
            ('watchlist_id', '=', self.id),
            ('date', '=', today)
        ])

        advice_data = {
            'watchlist_id': self.id,
            'date': today,
            'advice_type': advice_type,
            'reason': ', '.join(reason),
            'target_price': close_prices[-1],  # 使用最新收盤價作為目標價格
            'confidence': confidence
        }

        if advice:
            advice.write(advice_data)
        else:
            self.env['stock.watchlist.advice'].create(advice_data)

    def _calculate_rsi(self, prices, period=14):
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100./(1. + rs)

        for i in range(period, len(prices)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(period-1) + upval)/period
            down = (down*(period-1) + downval)/period
            rs = up/down
            rsi[i] = 100. - 100./(1. + rs)

        return rsi[-1]

    def generate_all_advice(self):
        watchlists = self.search([])
        for watchlist in watchlists:
            watchlist.generate_advice()

    def predict_stock_movement(self):
        self.ensure_one()
        prediction_model = self.env['stock.prediction'].search([('watchlist_id', '=', self.id)], limit=1)

        if not prediction_model:
            prediction_model = self.env['stock.prediction'].create({
                'watchlist_id': self.id,
            })

        prediction_model.train_model()
        prediction, confidence = prediction_model.make_prediction()

        self.write({
            'prediction': 'up' if prediction == 1 else 'down',
            'prediction_confidence': confidence * 100
        })

    def update_all_predictions(self):
        watchlists = self.search([])
        for watchlist in watchlists:
            watchlist.predict_stock_movement()

