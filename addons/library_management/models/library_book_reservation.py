from odoo import models, fields, api

class LibraryBookReservation(models.Model):
    _name = 'library.book.reservation'
    _description = '書籍預約'

    book_id = fields.Many2one('library.book', string='書籍', required=True)
    reserved_by = fields.Many2one('library.student', string='預約讀者', required=True)
    reservation_date = fields.Date(string='預約日期', default=fields.Date.context_today)
    state = fields.Selection([
        ('pending', '等待中'),
        ('notified', '已通知'),
        ('canceled', '已取消')],
        string='狀態', default='pending')

    @api.model
    def notify_next_reservation(self, book):
        """通知下一位預約的讀者書籍已可借閱"""
        next_reservation = self.search([('book_id', '=', book.id), ('state', '=', 'pending')], limit=1)
        if next_reservation:
            next_reservation.write({'state': 'notified'})
            book.message_post(body=f"書籍 {book.name} 已通知讀者 {next_reservation.reserved_by.name}，可借閱。")
            # 可以在這裡設計發送通知的邏輯，例如通過郵件或訊息
