#-*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError

class Tags(models.Model):
    _name         = 'todo.task.tag'
    _parent_store = True
    #_parent_name  = 'parent_id'
    
    name = fields.Char('Name')
    parent_id     = fields.Many2one('todo.task.tag','Parent Tag', ondelete='restrict')
    parent_left   = fields.Integer('Parent Left', index=True)
    parent_right  = fields.Integer('Parent  Right', index=True)
    child_ids = fields.One2many('todo.task.tag', 'parent_id', 'Child Tags')
    
class Stage(models.Model):
    _name = 'todo.task.stage'
    _order = 'sequence,name'
    _rec_name = 'name'  # predeterminado
    _table = 'todo_task_stage' # predeterminado
    
    name = fields.Char('Name', size=40, translate=True)
    sequence = fields.Integer('Sequence')
    #Stage class relación con Tasks:
    desc  = fields.Text('Description')
    docs  = fields.Html('Documentation')
    tasks = fields.One2many('todo.task',# modelo relacionado
                            'stage_id',# campo para "este" en el modelo relacionado
                            'Tasks in this stage')
    state = fields.Selection([('draft','New'),('open','Started'), ('done','Closed')],'State')
    # Campos numéricos:
    sequence      = fields.Integer('Sequence')
    perc_complete = fields.Float('% Complete',(3,2))
    # Campos de fecha:
    date_effective = fields.Date('Effective Date')
    date_changed   = fields.Datetime('Last Changed')
    # Otros campos:
    fold  = fields.Boolean('Folded?')
    image = fields.Binary('Image')
    
class TodoTask(models.Model):
    _inherit = 'todo.task'
    
    # TodoTask class: Task  <-> relación Tag (forma larga):
    tag_ids = fields.Many2many(comodel_name='todo.task.tag', # modelo relacionado
                           relation='todo_task_tag_rel', # nombre de la tabla de relación
                           column1='task_id', # campo para "este" registro
                           column2='tag_id', # campo para "otro" registro
                           string='Tasks')
    stage_id = fields.Many2one('todo.task.stage', 'Stage')
    #refers_to = fields.Reference(referencable_models, 'Refers to')
    stage_fold = fields.Boolean(
        string   = 'Stage Folded?',
        compute  ='_compute_stage_fold',
        search   ='_search_stage_fold',
        inverse  ='_write_stage_fold')
    stage_state = fields.Selection(related='stage_id.state', string='Stage State')
    refers_to = fields.Reference([('res.user', 'User'),('res.partner', 'Partner')], 'Refers to')
    
    _sql_constraints = [
        ('todo_task_name_uniq',
         'UNIQUE (name, user_id, active)',
         'Task title must be unique!')]
        
    @api.one
    @api.depends('stage_id.fold')
    def _compute_stage_fold(self):
        self.stage_fold = self.stage_id.fold
        
    def _search_stage_fold(self, operator, value):
        return [('stage_id.fold', operator, value)]

    def _write_stage_fold(self):
        self.stage_id.fold = self.stage_fold
    
    @api.one
    @api.constrains('name')
    def _check_name_size(self):
        if len(self.name) < 5:
             raise ValidationError('Must have 5 chars!')

    




