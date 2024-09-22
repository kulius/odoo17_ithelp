from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    student_id = fields.Many2one('library.student', string='學生資料', help='此用戶對應的學生資料')
