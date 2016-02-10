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
        if self.order_id:
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
            security_key = False
            user = self.env['hr.employee'].search([('state_id', '=', self.partner_id.state_id.id)])
            if user:
                task_data = self.env['project.task'].read_group([('user_id', '!=', False)],['user_id'], ['user_id'])
                mapped_data = dict([(task['user_id'][0], task['user_id_count']) for task in task_data])
                if mapped_data:
                    user_id = min(mapped_data, key=mapped_data.get)
                    security_key = self.env['hr.employee'].browse(user_id).security_key
            defaults.update({'name': name, 'project_id': project_id, 
                             'user_id': user_id, 'picking_id': self.id, 
                             'partner_id': self.partner_id.id,
                             'security_key': security_key})
            task = self.env['project.task'].create(defaults)
            self.task_id = task.id
        return res
    
    @api.multi
    @api.depends('group_id')
    def _compute_order_id(self):
        for picking in self:
            picking.order_id = self.env['sale.order'].search([('procurement_group_id', '=', picking.group_id.id)]) if picking.group_id else False

    order_id = fields.Many2one('sale.order', compute='_compute_order_id', string='Order associated to this picking', copy=False, store=True)
    task_id = fields.Many2one("project.task", 'Related Task', copy=False)
    
class res_users(models.Model):
    _inherit = 'res.users'

    @api.one
    def _get_stat(self):
        task_obj = self.env['project.task']
        today = fields.Date.context_today(self)
        self.total = len(task_obj.search([('user_id', '=', self.id), ('date_assign', '>=', today)]))
        self.new = len(task_obj.search([('user_id', '=', self.id), ('delivery_status', '=', 'new'), ('date_assign', '>=', today)]))
        self.out_for_delivery = len(task_obj.search([('user_id', '=', self.id), ('delivery_status', '=', 'out_for_delivery'), ('date_assign', '>=', today)]))
        self.delivered = len(task_obj.search([('user_id', '=', self.id), ('delivery_status', '=', 'delivered'), ('date_assign', '>=', today)]))
        self.undelivered = len(task_obj.search([('user_id', '=', self.id), ('delivery_status', '=', 'undelivered'), ('date_assign', '>=', today)]))
        self.undelivered_attempted = len(task_obj.search([('user_id', '=', self.id), ('delivery_status', '=', 'undelivered_attempted'), ('date_assign', '>=', today)]))
        self.out_for_pickup = len(task_obj.search([('user_id', '=', self.id), ('delivery_status', '=', 'out_for_pickup'), ('date_assign', '>=', today)]))
        self.picked = len(task_obj.search([('user_id', '=', self.id), ('delivery_status', '=', 'picked'), ('date_assign', '>=', today)]))
        self.unpicked = len(task_obj.search([('user_id', '=', self.id), ('delivery_status', '=', 'unpicked'), ('date_assign', '>=', today)]))
        self.unpicked_attempted = len(task_obj.search([('user_id', '=', self.id), ('delivery_status', '=', 'unpicked_attempted'), ('date_assign', '>=', today)]))

    total = fields.Integer('Total', compute=_get_stat, default=0)
    new = fields.Integer('New', compute=_get_stat, default=0)
    out_for_delivery = fields.Integer('Out for Delivery', compute=_get_stat, default=0)
    delivered = fields.Integer('Delivered', compute=_get_stat, default=0)
    undelivered = fields.Integer('Un-Delivered', compute=_get_stat, default=0)
    undelivered_attempted = fields.Integer('Un-Delivered Attempted', compute=_get_stat, default=0)
    out_for_pickup = fields.Integer('Out for Pickup', compute=_get_stat, default=0)
    picked = fields.Integer('Picked', compute=_get_stat, default=0)
    unpicked = fields.Integer('Un-Picked', compute=_get_stat, default=0)
    unpicked_attempted = fields.Integer('Un-Picked Attempted', compute=_get_stat, default=0)
    
class project(models.Model):
    _inherit = "project.project"
    
    state_id = fields.Many2one("res.country.state", 'Area')
    
class hr_employee(models.Model):
    _inherit = "hr.employee"
    
    state_id = fields.Many2one("res.country.state", 'Area')
    security_key = fields.Char('Security key to update')
    
class project_task(models.Model):
    _inherit = "project.task"
    
    @api.one
    def _get_items_total(self):
        if self.picking_id and self.picking_id.order_id:
            order_id = self.picking_id.order_id
            self.items_total = len(order_id.mapped('order_line.id'))

    picking_id = fields.Many2one("stock.picking", 'Delivery Order', copy=False)
    picking_type = fields.Selection(string='Picking Type', related='picking_id.picking_type_code')
    partner_name = fields.Char(string='Customer Name', related='partner_id.name')
    partner_street = fields.Char(string='Street', related='partner_id.street')
    partner_street2 = fields.Char(string='Street2', related='partner_id.street2')
    partner_state = fields.Char(string='State', related='partner_id.state_id.name')
    partner_zip = fields.Char(string='Zip', related='partner_id.zip')
    partner_country = fields.Char(string='Country', related='partner_id.country_id.name')
    partner_mobile = fields.Char(string='Mobile', related='partner_id.mobile')
    stage_name = fields.Char(string='Stage Name', related='stage_id.name')
    delivered_to = fields.Char(string='Delivered To', copy=False)
    signature = fields.Binary(string='Signature', copy=False)
    order_id = fields.Many2one(string='Sale Order', related='picking_id.order_id')
    amount_total = fields.Monetary(string='Total Amount', related='picking_id.order_id.amount_total')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    items_total = fields.Integer('Total No of items ordered', compute=_get_items_total, default=0)
    security_key = fields.Char('Security key to update')
    payment_mode = fields.Selection([
                                    ('cod', 'Cash on Delivery'),
                                    ('online_payment', 'Online Payment'), 
                                    ], string='Payment Mode',
                                   copy=False, default='cod')
    cash_collected = fields.Float(string='Cash Collected')
    delivery_status = fields.Selection([
                                        ('new', 'Task Created'),
                                        ('out_for_delivery', 'Out for Delivery'), 
                                        ('delivered', 'Delivered'),
                                        ('undelivered', 'Un-Delivered'),
                                        ('undelivered_attempted', 'Un-Delivered Attempted'),
                                        ('out_for_pickup', 'Out for Pickup'), 
                                        ('picked', 'Picked'),
                                        ('unpicked', 'Un-Picked'),
                                        ('unpicked_attempted', 'Un-Picked Attempted')
                                        ], string='Delivery/Pickup Status',
                                       copy=False, default='new')
    delivery_location = fields.Char(string='Delivery Location')
    received_by = fields.Char(string='Received By')
    recipient_name = fields.Char(string='Recipient name')
    customer_feedback = fields.Char(string='Customer Feedback', size=512)
    
class project_task_error(models.Model):
    _name = "project.task.error"
    _description = "User Error Reporting"
    
    name = fields.Char(string='Error Subject')
    user_id = fields.Many2one("res.users", 'Reported User', copy=False)
    comments = fields.Text(string='Comments')