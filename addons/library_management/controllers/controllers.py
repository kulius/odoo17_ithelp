from odoo import http
from odoo.http import request

class LibraryWebsite(http.Controller):

    @http.route(['/library/books'], type='http', auth='public', website=True)
    def list_books(self, search='', **kwargs):
        domain = []
        if search:
            domain += ['|', '|',
                       ('name', 'ilike', search),
                       ('author', 'ilike', search),
                       ('isbn', 'ilike', search)]
        books = request.env['library.book'].search(domain)
        return request.render('library_management.library_book_list_template', {
            'books': books,
            'search': search,
        })

    @http.route(['/library/book/<model("library.book"):book>'], type='http', auth='public', website=True)
    def view_book(self, book, **kwargs):
        return request.render('library_management.library_book_detail_template', {
            'book': book,
        })
