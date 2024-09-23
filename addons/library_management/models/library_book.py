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


    @api.depends('is_borrowed')
    def is_book_available(self):
        """
        檢查書籍當前是否可借閱。
        如果書籍已被借出，返回 False；如果可借，返回 True。
        """
        for record in self:
            if record.is_borrowed:
                record.message_post(body=f"書籍 {record.name} 已被借出。")
                raise exceptions.UserError(f'書籍 {record.name} 已被借出，無法借閱。')
            return True

    def action_check_availability(self):
        """
        行動按鈕：檢查書籍的可用性，顯示是否可借。
        """
        for record in self:
            if record.is_borrowed:
                raise exceptions.UserError(f'書籍 {record.name} 已被借出。')
            else:
                raise exceptions.UserError(f'書籍 {record.name} 可借閱。')

    def action_borrow(self):
        """
        當書籍可借閱時，允許讀者借閱，並記錄借閱信息
        """
        for record in self:
            if record.is_borrowed:
                raise exceptions.UserError(f"書籍 {record.name} 已被借出，無法再次借閱。")

            # 檢查是否已關聯借閱學生
            if not record.borrowed_by:
                raise exceptions.UserError('請選擇借閱的學生。')

            # 更新書籍狀態為已借出，並記錄借閱日期
            record.is_borrowed = True
            record.borrow_date = date.today()

            # 生成消息記錄
            record.message_post(
                body=f"書籍 {record.name} 已於 {record.borrow_date} 被學生 {record.borrowed_by.name} 借閱。")