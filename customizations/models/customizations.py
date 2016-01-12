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
        fields_list = self.env['project.task'].fields_get()
        defaults = self.env['project.task'].with_context({'active_ids':self._ids, 'active_id': self.id}).default_get(fields_list)
        name = 'New Task'
        if self.group_id:
            order_id = self.env['sale.order'].search([('procurement_group_id', '=', self.group_id.id)])
            if order_id:
                name = order_id.name
        project_id = False
        project = self.env['project.project'].search([('state_id', '=', self.partner_id.state_id.id)])
        if project:
            project_id = project.id
        user_id = False
        user = self.env['hr.employee'].search([('state_id', '=', self.partner_id.state_id.id)])
        if user:
            task_data = self.env['project.task'].read_group([('stage_id.closed', '=', False), ('user_id', '!=', False)],['user_id'], ['user_id'])
            mapped_data = dict([(task['user_id'][0], task['user_id_count']) for task in task_data])
            if mapped_data:
                user_id = min(mapped_data, key=mapped_data.get)
        defaults.update({'name': name, 'project_id': project_id, 'user_id': user_id, 'picking_id': self.id, 'partner_id': self.partner_id.id})
        task = self.env['project.task'].create(defaults)
        self.task_id = task.id
        return res
    
    task_id = fields.Many2one("project.task", 'Related Task')
    
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
    
    
class project_task(models.Model):
    _inherit = "project.task"
    
    picking_id = fields.Many2one("stock.picking", 'Delivery Order')
    partner_name = fields.Char(string='Customer Name', related='partner_id.name')
    partner_street = fields.Char(string='Street', related='partner_id.street')
    partner_street2 = fields.Char(string='Street2', related='partner_id.street2')
    partner_state = fields.Char(string='State', related='partner_id.state_id.name')
    partner_zip = fields.Char(string='Zip', related='partner_id.zip')
    partner_country = fields.Char(string='Country', related='partner_id.country_id.name')
    partner_mobile = fields.Char(string='Mobile', related='partner_id.mobile')
    stage_name = fields.Char(string='Stage Name', related='stage_id.name')
    delivered_to = fields.Char(string='Delivered To')
    signature = fields.Binary(string='Signature')