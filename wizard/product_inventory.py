from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import tools

class stock_change_product_qty(osv.osv_memory):
    _inherit = "stock.change.product.qty"
    _columns = {
	'adjustment_reference': fields.char('Adjustment Reference'),
    }


    #Once again it because necessary to override entire method
    #You cant do action before because ids is a wizard object
    #You cant do after because the inventory is done
    #You cant do anything anywhere because everything is compressed into one method
    def change_product_qty(self, cr, uid, ids, context=None):
        """ Changes the Product Quantity by making a Physical Inventory.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        inventory_obj = self.pool.get('stock.inventory')
        inventory_line_obj = self.pool.get('stock.inventory.line')

        for data in self.browse(cr, uid, ids, context=context):
            if data.new_quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Quantity cannot be negative.'))
            ctx = context.copy()
            ctx['location'] = data.location_id.id
            ctx['lot_id'] = data.lot_id.id
            inventory_id = inventory_obj.create(cr, uid, {
		#Its sort of redundant to put INV in the stock inventory name
		#because we already know its an inventory!
		#Additionally, lines end up like this in stock.move INV: INV: (stupid)
		'name': data.adjustment_reference or data.product_id.name,
#                'name': _('INV: %s') % data.tools.ustr(data.product_id.name),
                'product_id': data.product_id.id,
                'location_id': data.location_id.id,
                'lot_id': data.lot_id.id}, context=context)
            product = data.product_id.with_context(location=data.location_id.id, lot_id= data.lot_id.id)
            th_qty = product.qty_available
            line_data = {
                'inventory_id': inventory_id,
                'product_qty': data.new_quantity,
                'location_id': data.location_id.id,
                'product_id': data.product_id.id,
                'product_uom_id': data.product_id.uom_id.id,
                'theoretical_qty': th_qty,
                'prod_lot_id': data.lot_id.id
            }
            inventory_line_obj.create(cr , uid, line_data, context=context)
            inventory_obj.action_done(cr, uid, [inventory_id], context=context)
        return {}



