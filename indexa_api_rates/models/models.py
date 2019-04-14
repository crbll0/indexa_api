# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta
import logging

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

BANXICO_DATE_FORMAT = '%Y-%m-%d'

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    indexa_currency_interval_unit = fields.Selection([
        ('manually', 'Manually'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')],
        default='manually', string='Interval Unit')
    indexa_currency_next_execution_date = fields.Date(string="Next Execution Date")
    indexa_currency_provider = fields.Selection([
        ('bpd', 'Banco Popular Dominicano'),
        ('bnr', 'Banco de Reservas'),
        ('blh', 'Banco Lopez de Haro'),
        ('bpr', 'Banco del Progreso'),
        ('bsc', 'Banco Santa Cruz'),
        ('bdi', 'Banco BDI'),
        ('bpm', 'Banco Promerica'),
        ('bvm', 'Banco Vimenca'),
    ], default='bpd', string='Service Provider')
    last_indexa_sync_date = fields.Date(string="Last Sync Date", readonly=True)

    @api.multi
    def indexa_update_currency_rates(self):
        ''' This method is used to update all currencies given by the provider.
        It calls the parse_function of the selected exchange rates provider automatically.

        For this, all those functions must be called _parse_xxx_data, where xxx
        is the technical name of the provider in the selection field. Each of them
        must also be such as:
            - It takes as its only parameter the recordset of the currencies
              we want to get the rates of
            - It returns a dictionary containing currency codes as keys, and
              the corresponding exchange rates as its values. These rates must all
              be based on the same currency, whatever it is. This dictionary must
              also include a rate for the base currencies of the companies we are
              updating rates from, otherwise this will result in an error
              asking the user to choose another provider.

        :return: True if the rates of all the records in self were updated
                 successfully, False if at least one wasn't.
        '''
        rslt = True
        active_currencies = self.env['res.currency'].search([])
        for (indexa_currency_provider, companies) in self._group_by_bank().items():
            dict_result = self.get_currency_rates(active_currencies, indexa_currency_provider)

            if dict_result == False:
                # We check == False, and don't use bool conversion, as an empty
                # dict can be returned, if none of the available currencies is supported by the provider
                _logger.warning(_('Unable to connect to the online exchange rate platform %s. The web service may be temporary down.') % indexa_currency_provider)

                rslt = False
            else:
                companies.indexa_generate_currency_rates(dict_result)
                companies.write({'last_indexa_sync_date': fields.Date.today()})

        return rslt

    def _group_by_bank(self):
        """ Returns a dictionnary grouping the companies in self by currency
        rate provider. Companies with no provider defined will be ignored."""
        rslt = {}
        for company in self:
            if not company.indexa_currency_provider:
                continue

            if rslt.get(company.indexa_currency_provider):
                rslt[company.indexa_currency_provider] += company
            else:
                rslt[company.indexa_currency_provider] = company
        return rslt

    def indexa_generate_currency_rates(self, parsed_data):
        """ Generate the currency rate entries for each of the companies, using the
        result of a parsing function, given as parameter, to get the rates data.

        This function ensures the currency rates of each company are computed,
        based on parsed_data, so that the currency of this company receives rate=1.
        This is done so because a lot of users find it convenient to have the
        exchange rate of their main currency equal to one in Odoo.
        """
        Currency = self.env['res.currency']
        CurrencyRate = self.env['res.currency.rate']

        today = fields.Date.today()
        for company in self:
            for currency, (rate, date_rate) in parsed_data.items():
                rate_value = 1/rate

                currency_object = Currency.search([('name','=',currency)])
                already_existing_rate = CurrencyRate.search([
                    ('currency_id', '=', currency_object.id),
                    ('name', '=', date_rate),
                    ('company_id', '=', company.id)
                ])
                if already_existing_rate:
                    already_existing_rate.rate = rate_value
                else:
                    CurrencyRate.create({'currency_id': currency_object.id,
                                         'rate': rate_value,
                                         'name': date_rate,
                                         'company_id': company.id})

    def get_currency_rates(self, available_currencies, indexa_currency_provider):
        ''' Parses the data returned in xml by FTA servers and returns it in a more
        Python-usable form.'''

        parameter = self.env['ir.config_parameter']
        indexa_api_url = parameter.search([('key', '=', 'indexa_api_url')])
        indexa_api_token = parameter.search([('key', '=', 'indexa_api_token')])

        if not indexa_api_url or not indexa_api_url.value:
            raise UserError('Indexa API URL is not defined')

        if not indexa_api_token or not indexa_api_token.value:
            raise UserError('Indexa API TOKEN is not defined')

        url = indexa_api_url.value
        token = indexa_api_token.value

        today = fields.Date.today()

        url_full = '{url}/rates?bank={bank}&date={date:%Y-%m-%d}'.format(url=url, bank=indexa_currency_provider,
                                                                         date=today)

        try:
            request = requests.get(url_full, headers={'x-access-token': token})
        except:
            return False

        codes = {
            'dollarsellrate': 'USD',
            'eurosellrate': 'EUR',
        }

        rates_dict = {}
        available_currency_names = available_currencies.mapped('name')

        if request.ok:
            for i in request.json()['data']:
                if i['name'] in codes.keys():
                    currency_code = codes[i['name']]

                    if currency_code in available_currency_names:
                        rates_dict[currency_code] = (i['rate'], today)

        return rates_dict

    @api.model
    def run_indexa_update_currency(self):
        """ This method is called from a cron job to update currency rates.
        """
        records = self.search([('indexa_currency_next_execution_date', '<=', fields.Date.today())])
        if records:
            to_update = self.env['res.company']
            for record in records:
                if record.indexa_currency_interval_unit == 'daily':
                    next_update = relativedelta(days=+1)
                elif record.indexa_currency_interval_unit == 'weekly':
                    next_update = relativedelta(weeks=+1)
                elif record.indexa_currency_interval_unit == 'monthly':
                    next_update = relativedelta(months=+1)
                else:
                    record.indexa_currency_next_execution_date = False
                    continue
                record.indexa_currency_next_execution_date = datetime.date.today() + next_update
                to_update += record
            to_update.indexa_update_currency_rates()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    indexa_currency_interval_unit = fields.Selection(related="company_id.indexa_currency_interval_unit", readonly=False)
    indexa_currency_provider = fields.Selection(related="company_id.indexa_currency_provider", readonly=False)
    indexa_currency_next_execution_date = fields.Date(related="company_id.indexa_currency_next_execution_date", readonly=False)
    last_indexa_sync_date = fields.Date(related="company_id.last_indexa_sync_date", readonly=False)

    @api.onchange('indexa_currency_interval_unit')
    def onchange_indexa_currency_interval_unit(self):
        #as the onchange is called upon each opening of the settings, we avoid overwriting
        #the next execution date if it has been already set
        if self.company_id.indexa_currency_next_execution_date:
            return
        if self.currency_interval_unit == 'daily':
            next_update = relativedelta(days=+1)
        elif self.currency_interval_unit == 'weekly':
            next_update = relativedelta(weeks=+1)
        elif self.currency_interval_unit == 'monthly':
            next_update = relativedelta(months=+1)
        else:
            self.indexa_currency_next_execution_date = False
            return

        self.indexa_currency_next_execution_date = datetime.date.today() + next_update

    def indexa_update_currency_rates_manually(self):
        self.ensure_one()
        if not (self.company_id.indexa_update_currency_rates()):
            raise UserError(_('Unable to connect to the online exchange rate platform. The web service may be temporary down. Please try again in a moment.'))
