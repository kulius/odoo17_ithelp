from odoo import models, fields, api

class LibraryStudent(models.Model):
    _name = 'library.student'
    _description = '學生資料'

    name = fields.Char(string='姓名', required=True)
    student_number = fields.Char(string='學號', required=True, unique=True)
    class_name = fields.Char(string='班級')
    email = fields.Char(string='電子郵件')
    phone = fields.Char(string='電話')
    user_id = fields.Many2one('res.users', string='系統用戶', help='該學生對應的系統用戶')

    @api.model
    def create(self, vals):
        # 在創建學生時自動創建用戶帳號
        user_vals = {
            'name': vals['name'],
            'login': vals['name'],  # 以學生的電子郵件作為登入名
            'email': vals['email'],
            'password': vals['name'],  # 以學生的電子郵件作為密碼
            'partner_id': self.env['res.partner'].create({
                'name': vals['name'],
                'email': vals['email']
            }).id,
        }
        user = self.env['res.users'].create(user_vals)
        vals['user_id'] = user.id  # 將創建的用戶關聯到學生資料

        # 創建學生
        student = super(LibraryStudent, self).create(vals)

        # 回寫學生ID到res.users的student_id字段
        user.write({'student_id': student.id})

        return student
