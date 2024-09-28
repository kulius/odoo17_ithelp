from odoo import models, fields, api, exceptions
from datetime import date, timedelta

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
    reservation_ids = fields.One2many('library.book.reservation', 'book_id', string='預約列表')
    loan_ids = fields.One2many('library.book.loan', 'book_id', string='借閱記錄')

    def action_reserve(self):
        """
        當書籍已借出時，允許讀者預約該書籍，並將其加入預約隊列。
        """
        if not self.is_borrowed:
            raise exceptions.UserError('書籍目前可借閱，無需預約。')

        reservation = self.env['library.book.reservation'].create({
            'book_id': self.id,
            'reserved_by': self.env.user.student_id.id,  # 使用當前登錄的讀者
        })
        self.message_post(body=f"書籍 {self.name} 已由讀者 {reservation.reserved_by.name} 預約。")

        # 返回成功的訊息給用戶
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '預約成功',
                'message': f'書籍 {self.name} 已成功預約。',
                'type': 'success',  # success, warning, info, danger
                'sticky': False,  # 如果設置為 True，消息不會自動消失
            }
        }

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

            # 設定預計歸還日期，假設借閱期為14天
            expected_return = record.borrow_date + timedelta(days=14)

            # 創建借閱記錄
            self.env['library.book.loan'].create({
                'book_id': record.id,
                'student_id': record.borrowed_by.id,
                'loan_date': record.borrow_date,
                'expected_return_date': expected_return,
            })

            # 生成消息記錄
            record.message_post(
                body=f"書籍 {record.name} 已於 {record.borrow_date} 被學生 {record.borrowed_by.name} 借閱，預計歸還日期為 {expected_return}。")

    def action_return(self):
        """
        書籍歸還操作：更新書籍狀態為「未借出」，記錄歸還日期，並更新借閱記錄。
        """
        for record in self:
            if not record.is_borrowed:
                raise exceptions.UserError('書籍尚未借出，無法執行歸還操作。')

            # 更新書籍狀態為未借出
            record.is_borrowed = False
            record.return_date = date.today()

            # 更新借閱記錄
            loan = self.env['library.book.loan'].search([
                ('book_id', '=', record.id),
                ('student_id', '=', record.borrowed_by.id),
                ('state', '=', 'ongoing')
            ], limit=1)
            if loan:
                loan.actual_return_date = record.return_date
                loan.state = 'returned'

            # 清空借閱人信息
            record.borrowed_by = None

            # 生成消息記錄
            record.message_post(body=f"書籍 {record.name} 已於 {record.return_date} 歸還。")

            # 通知下一位預約的讀者
            next_reservation = self.env['library.book.reservation'].search([
                ('book_id', '=', record.id),
                ('state', '=', 'pending')
            ], order='reservation_date asc', limit=1)

            if next_reservation:
                next_reservation.write({'state': 'notified'})
                record.message_post(body=f"書籍 {record.name} 已通知讀者 {next_reservation.reserved_by.name} 可借閱。")
                # 這裡可以加入郵件或訊息通知功能

            return True