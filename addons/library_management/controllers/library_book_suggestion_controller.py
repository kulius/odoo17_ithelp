from odoo import http
from odoo.http import request

class LibraryBookSuggestionController(http.Controller):

    @http.route(['/my/booksuggestions'], type='http', auth='user', website=True)
    def my_book_suggestions(self, **kwargs):
        suggestions = request.env['library.book.suggestion'].sudo().search([('suggested_by', '=', request.env.user.id)])
        return request.render('library_management.library_book_suggestion_template', {
            'suggestions': suggestions,
        })

    @http.route(['/my/book_suggestions/new'], type='http', auth='user', website=True)
    def new_book_suggestion(self, **kwargs):
        return request.render('library_management.library_book_suggestion_form_template')


    @http.route(['/my/book_suggestions/submit'], type='http', auth='user', methods=['POST'], website=True)
    def submit_book_suggestion(self, **post):
        vals = {
            'name': post.get('name'),
            'author': post.get('author'),
            'isbn': post.get('isbn'),
            'suggested_by': request.env.user.id,
        }
        request.env['library.book.suggestion'].sudo().create(vals)
        return request.render('library_management.library_book_suggestion_thankyou_template')
