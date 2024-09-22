from odoo import models, fields

class LibraryStudent(models.Model):
    _name = 'library.student'
    _description = '學生資料'

    name = fields.Char(string='姓名', required=True)
    student_number = fields.Char(string='學號', required=True, unique=True)
    class_name = fields.Char(string='班級')
    email = fields.Char(string='電子郵件')
    phone = fields.Char(string='電話')
