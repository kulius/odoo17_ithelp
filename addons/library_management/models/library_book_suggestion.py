from odoo import models, fields, api
from datetime import date

class LibraryBookSuggestion(models.Model):
    _name = 'library.book.suggestion'
    _description = '購書建議'

    name = fields.Char(string='書名', required=True)
    author = fields.Char(string='作者')
    isbn = fields.Char(string='ISBN')
    suggested_by = fields.Many2one('res.users', string='建議人', default=lambda self: self.env.user, readonly=True)
    suggestion_date = fields.Date(string='建議日期', default=fields.Date.context_today, readonly=True)
    state = fields.Selection([
        ('submitted', '已提交'),
        ('in_progress', '處理中'),
        ('accepted', '已採納'),
        ('rejected', '已拒絕')],
        string='狀態', default='submitted', tracking=True)
    note = fields.Text(string='備註')
