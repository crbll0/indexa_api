# -*- coding: utf-8 -*-

import requests
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IndexaAPiFuels(models.Model):
    _name = 'indexa.api.fuels'
    _inherit = ['mail.thread']
    _description = 'Indexa API Fuels'

    name = fields.Char()
    product_id = fields.Many2one('product.product', string="Product",
                                 track_visibility='always', required=1)
    fuel_type = fields.Selection([
        ('GasolinaPremium', 'Gasolina Premium'),
        ('GasolinaRegular', 'Gasolina Regular'),
        ('GasoilOptimo', 'Gasoil Optimo'),
        ('GasoilRegular', 'Gasoil Regular'),
        ('Kerosene', 'Kerosene'),
        ('GasNaturalVehicular(GNV)', 'Gas Natural Vehicular (GNV)'),
        ('GasLicuadodePetr\xf3leo(GLP)', 'Gas Licuadode Petroleo (GLP)'),
    ], string='Fuel Type', track_visibility='always',  required=1)

    last_price = fields.Float(string='Last Price',
                              track_visibility='always', readonly=1)

    update_in = fields.Selection([
        ('product', 'Product'),
        ('pricelist', 'PriceList'),
    ], default='product', track_visibility='always')

    pricelist_id = fields.Many2one('product.pricelist', string='PriceList',
                                   track_visibility='always')

    @api.multi
    def get_fuel_price(self):
        """EXAMPLE
        >>> r = requests.get('https://api.indexa.do/api/fuels?date=2018-12-15', headers={"x-access-token": "x71FDDDA39D66Ex"})

        If Response is 201 [ok]
        >>> r.ok
        True
        >>> r.json()
        {u'status': u'success',
         u'data': [
            {u'date': u'2018-12-15', u'price': 162.8, u'name': u'Kerosene'},
            {u'date': u'2018-12-15', u'price': 184.3, u'name': u'GasoilOptimo'},
            {u'date': u'2018-12-15', u'price': 171.9, u'name': u'GasoilRegular'},
            {u'date': u'2018-12-15', u'price': 199.9, u'name': u'GasolinaRegular'},
            {u'date': u'2018-12-15', u'price': 28.97, u'name': u'GasNaturalVehicular(GNV)'},
            {u'date': u'2018-12-15', u'price': 107.6, u'name': u'GasLicuadodePetr\xf3leo(GLP)'},
            {u'date': u'2018-12-15', u'price': 213.7, u'name': u'GasolinaPremium'}
        ]}

        If Response is not 201 [no ok]
        >>> r.ok
        False
        >>> r.json()
        {u'status': u'error', u'message': u'Your token is not registered'}

        """

        parameter = self.env['ir.config_parameter']
        indexa_api_url = parameter.search([('key', '=', 'indexa_api_url')])
        indexa_api_token = parameter.search([('key', '=', 'indexa_api_token')])

        if not indexa_api_url or not indexa_api_url.value:
            raise UserError('Indexa API URL is not defined')

        if not indexa_api_token or not indexa_api_token.value:
            raise UserError('Indexa API TOKEN is not defined')

        pricelist_item = self.env['product.pricelist.item']

        #
        # days_back contiene como Key los dias (1 = Lunes) y como Value
        # los dias que tiene que retroceder para obtener la fecha correcta
        # por si la accion no se ejecuta un Dia sabado.
        #
        # La accion debe de ejecutarse los sabados ya que esos dias
        # industria y comercio actualiza la lista de precio de los combustibles.
        #

        days_back = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 7: 1}

        date_from = fields.Date.today()
        if date_from.isoweekday() != 6:
            back = days_back[date_from.isoweekday()]
            date_from = fields.Date.subtract(date_from, days=back)

        date_to = fields.Date.add(date_from, days=6)

        url = indexa_api_url.value
        token = indexa_api_token.value

        url_full = '{url}/fuels?date={date:%Y-%m-%d}'.format(url=url,
                                                            date=date_from)
        request = requests.get(url_full, headers={'x-access-token': token})

        if request.ok:
            for i in request.json()['data']:
                objs = self.search([('fuel_type', '=', i['name'])])

                if not objs:
                    continue

                for o in objs:
                    o.last_price = i['price']
                    
                    if o.update_in == 'product':
                        o.product_id.lst_price = i['price']

                    elif o.update_in == 'pricelist':
                        pricelist_item.create({
                                'applied_on': '1_product',
                                'product_tmpl_id': o.product_id.id,
                                'compute_price': 'fixed',
                                'fixed_price': float(i['price']),
                                'date_start': str(date_from),
                                'date_end': str(date_to),
                                'pricelist_id': o.pricelist_id.id,
                            }
                        )
        else:
            raise UserError('Error: %s' % request.text())