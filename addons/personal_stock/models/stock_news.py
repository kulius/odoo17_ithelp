from odoo import models, fields, api
from textblob import TextBlob
import jieba
import re

class StockNews(models.Model):
    _name = 'stock.news'
    _description = '股票新聞和公告'

    watchlist_id = fields.Many2one('stock.watchlist', string='觀察名單', compute='_compute_watchlist', store=True)
    title = fields.Char('標題')
    content = fields.Text('內容摘要')
    source = fields.Char('來源')
    publish_date = fields.Datetime('發布時間')
    news_type = fields.Selection([
        ('financial_report', '財務報告'),
        ('major_event', '重大事件'),
        ('product_launch', '產品發布'),
        ('market_analysis', '市場分析'),
        ('other', '其他')
    ], string='新聞類型', compute='_compute_news_type', store=True)
    importance = fields.Selection([
        ('high', '高'),
        ('medium', '中'),
        ('low', '低')
    ], string='重要性', compute='_compute_importance', store=True)
    url = fields.Char('原文連結')

    @api.model
    def create(self, vals):
        # 在這裡可以添加創建新聞時的額外邏輯
        return super(StockNews, self).create(vals)

    @api.depends('title', 'content')
    def _compute_watchlist(self):
        for news in self:
            watchlists = self.env['stock.watchlist'].search([])
            for watchlist in watchlists:
                if watchlist.name in news.title or watchlist.stock_code in news.title:
                    news.watchlist_id = watchlist.id
                    break

    @api.depends('title', 'content')
    def _compute_importance(self):
        important_keywords = ['重大', '突破', '創新高', '創新低', '大漲', '大跌', '收購', '合併', '破產', '違約']
        for news in self:
            importance_score = 0

            # 關鍵詞匹配
            text = news.title + ' ' + (news.content or '')
            for keyword in important_keywords:
                if keyword in text:
                    importance_score += 1

            # 情感分析
            blob = TextBlob(self.preprocess_text(text))
            sentiment = blob.sentiment.polarity
            if abs(sentiment) > 0.5:
                importance_score += 1

            # 根據分數設置重要性
            if importance_score >= 2:
                news.importance = 'high'
            elif importance_score == 1:
                news.importance = 'medium'
            else:
                news.importance = 'low'

    @api.depends('title', 'content')
    def _compute_news_type(self):
        type_keywords = {
            'financial_report': ['財報', '季報', '年報', '營收', '獲利'],
            'major_event': ['重大事件', '重大訊息', '重大決策', '重大交易'],
            'product_launch': ['新產品', '發表', '上市', '推出'],
            'market_analysis': ['市場分析', '產業趨勢', '市場預測', '經濟展望']
        }
        for news in self:
            text = news.title + ' ' + (news.content or '')
            preprocessed_text = self.preprocess_text(text)

            news_type = 'other'
            max_count = 0
            for type, keywords in type_keywords.items():
                count = sum(1 for keyword in keywords if keyword in preprocessed_text)
                if count > max_count:
                    max_count = count
                    news_type = type

            news.news_type = news_type

    def preprocess_text(self, text):
        # 移除特殊字符和數字
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        # 分詞
        words = jieba.cut(text)
        return ' '.join(words)