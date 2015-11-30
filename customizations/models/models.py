from openerp import models, fields, api

# class test(models.Model):
#     _name = 'test.test'
#
#     name = fields.Char(
#         string="Name",                   # Optional label of the field
#         compute="_compute_name_custom",  # Transform the fields in computed fields
#         store=True,                      # If computed it will store the result
#         select=True,                     # Force index on field
#         readonly=True,                   # Field will be readonly in views
#         inverse="_write_name",           # On update trigger
#         required=True,                   # Mandatory field
#         translate=True,                  # Translation enable
#         help='bla bla',                  # Help tooltip text
#         company_dependent=True,          # Transform columns to ir.property
#         search='_search_function',       # Custom search function mainly used with compute
#         default='A name',                # Default is now a keyword of a field
#         related='partner_id.name',       # fields.related
#       )
