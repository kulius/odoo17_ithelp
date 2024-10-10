from odoo import models, fields, api
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle  # 添加這行

class StockPrediction(models.Model):
    _name = 'stock.prediction'
    _description = '股票預測模型'

    watchlist_id = fields.Many2one('stock.watchlist', string='觀察名單', required=True)
    model = fields.Binary(string='模型數據', attachment=True)
    last_trained = fields.Datetime(string='最後訓練時間')

    def prepare_data(self):
        kline_data = self.env['stock.kline'].search([
            ('watchlist_id', '=', self.watchlist_id.id)
        ], order='date asc')

        df = pd.DataFrame({
            'date': kline_data.mapped('date'),
            'open': kline_data.mapped('open_price'),
            'high': kline_data.mapped('high_price'),
            'low': kline_data.mapped('low_price'),
            'close': kline_data.mapped('close_price'),
            'volume': kline_data.mapped('volume')
        })

        df['returns'] = df['close'].pct_change()
        df['target'] = np.where(df['returns'].shift(-1) > 0, 1, 0)

        df['sma5'] = df['close'].rolling(window=5).mean()
        df['sma20'] = df['close'].rolling(window=20).mean()
        df['rsi'] = self.calculate_rsi(df['close'])

        df = df.dropna()

        features = ['open', 'high', 'low', 'close', 'volume', 'sma5', 'sma20', 'rsi']
        X = df[features]
        y = df['target']

        return X, y

    def calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def train_model(self):
        X, y = self.prepare_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        self.model = pickle.dumps(model)
        self.last_trained = fields.Datetime.now()

        return accuracy

    def make_prediction(self):
        if not self.model:
            return None, 0

        model = pickle.loads(self.model)
        latest_data = self.prepare_data()[0].iloc[-1].values.reshape(1, -1)
        prediction = model.predict(latest_data)[0]
        confidence = model.predict_proba(latest_data)[0][prediction]

        return prediction, confidence