from openerp import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sale', 'Sale Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')])
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sale', 'Sale Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')])
    
class product_template(models.Model):
    _inherit = "product.template"
    
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    state = fields.Selection([
        ('draft', 'Draft PO'),
        ('purchase', 'Purchase Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
        ])
    
class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(stock_picking, self).do_transfer()
        return res
    
class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def _get_stat(self):
        user_obj = self.env['res.users']
        task_obj = self.env['project.task']
        user = user_obj.search([('partner_id', '=', self.id)])
        self.total = len(task_obj.search([('user_id', 'in', user.mapped('id'))]))
        self.not_closed = len(task_obj.search([('user_id', 'in', user.mapped('id')), ('stage_id.closed', '=', False)]))

    total = fields.Integer('Total', compute=_get_stat, default=0)
    not_closed = fields.Integer('Total', compute=_get_stat, default=0)
    
class project(models.Model):
    _inherit = "project.project"
    
    state_id = fields.Many2one("res.country.state", 'Area')
    
class hr_employee(models.Model):
    _inherit = "hr.employee"
    
    state_id = fields.Many2one("res.country.state", 'Area')
    