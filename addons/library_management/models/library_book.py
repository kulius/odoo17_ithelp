from odoo import models, fields, api, exceptions
from datetime import date

class LibraryBook(models.Model):
    _name = 'library.book'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '書籍資料'# 繼承 mail.thread 以啟用 message_post 功能

    name = fields.Char(string='書名', required=True)
    author = fields.Char(string='作者', required=True)
    isbn = fields.Char(string='ISBN', required=True)
    category_id = fields.Many2one('library.book.category', string='分類')
    is_borrowed = fields.Boolean(string='是否已借出', default=False, tracking=True)  # 開啟 tracking
    borrowed_by = fields.Many2one('library.student', string='借書學生', tracking=True)
    borrow_date = fields.Date(string='借出日期', readonly=True, tracking=True)
    return_date = fields.Date(string='歸還日期', readonly=True, tracking=True)

    def action_borrow(self):
        for record in self:
            if record.is_borrowed:
                raise exceptions.UserError('此書籍已借出，無法再次借出。')
            if not record.borrowed_by:
                raise exceptions.UserError('請選擇借書學生。')
            record.is_borrowed = True
            record.borrow_date = date.today()
            record.message_post(body=f'書籍 {record.name} 已於 {record.borrow_date} 借出給學生 {record.borrowed_by.name}。')

    def action_return(self):
        for record in self:
            if not record.is_borrowed:
                raise exceptions.UserError('此書籍尚未借出，無法歸還。')
            record.is_borrowed = False
            record.return_date = date.today()
            record.message_post(body=f'書籍 {record.name} 已於 {record.return_date} 歸還。')
