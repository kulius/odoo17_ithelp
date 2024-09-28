from odoo import http
from odoo.http import request

class LibraryWebsite(http.Controller):

    @http.route(['/library/books'], type='http', auth='public', website=True)
    def list_books(self, **kwargs):
        books = request.env['library.book'].search([])
        return request.render('library_management.library_book_list_template', {
            'books': books,
        })

    @http.route(['/library/book/<model("library.book"):book>'], type='http', auth='public', website=True)
    def view_book(self, book, **kwargs):
        return request.render('library_management.library_book_detail_template', {
            'book': book,
        })
