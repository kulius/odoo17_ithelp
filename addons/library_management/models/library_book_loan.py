from odoo import models, fields, api
from datetime import date, timedelta

class LibraryBookLoan(models.Model):
    _name = 'library.book.loan'
    _description = '書籍借閱記錄'

    book_id = fields.Many2one('library.book', string='書籍', required=True)
    student_id = fields.Many2one('library.student', string='學生', required=True)
    loan_date = fields.Date(string='借閱日期', default=fields.Date.context_today)
    expected_return_date = fields.Date(string='預計歸還日期', required=True)
    actual_return_date = fields.Date(string='實際歸還日期')
    state = fields.Selection([
        ('ongoing', '借出中'),
        ('returned', '已歸還'),
        ('overdue', '逾期'),
    ], string='狀態', compute='_compute_state', store=True, default='ongoing')

    @api.depends('expected_return_date', 'actual_return_date')
    def _compute_state(self):
        for record in self:
            if record.actual_return_date:
                record.state = 'returned'
            else:
                if record.expected_return_date and record.expected_return_date < date.today():
                    record.state = 'overdue'
                else:
                    record.state = 'ongoing'
    def send_overdue_notification(self):
        """
        向逾期未還的學生發送電子郵件通知
        """
        for record in self:
            if record.state == 'overdue':
                # 發送電子郵件給學生
                if record.student_id.email:
                    template = self.env.ref('library_management.mail_template_overdue_notification')
                    if template:
                        template.sudo().send_mail(record.id, force_send=True)
                    else:
                        # 如果沒有定義模板，可以直接使用 message_post
                        record.student_id.user_id.partner_id.message_post(
                            subject='逾期提醒',
                            body=f"親愛的 {record.student_id.name}，您借閱的書籍《{record.book_id.name}》已逾期未還，請盡快歸還。"
                        )

    def send_overdue_notifications(self):
        """
        排程動作：檢查逾期借閱並發送通知
        """
        overdue_loans = self.search([
            ('state', '=', 'overdue'),
            ('student_id.user_id', '!=', False)
        ])
        for loan in overdue_loans:
            loan.send_overdue_notification()
