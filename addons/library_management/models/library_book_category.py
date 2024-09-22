from odoo import models, fields

class LibraryBookCategory(models.Model):
    _name = 'library.book.category'
    _description = '書籍分類'

    name = fields.Char(string='分類名稱', required=True)
    description = fields.Text(string='描述')
