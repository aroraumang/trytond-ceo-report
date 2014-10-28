# -*- coding: utf-8 -*-
"""
    ceo_report.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from openlabs_report_webkit import ReportWebkit

from trytond.pool import Pool
from trytond.model import ModelView, fields, ModelSQL, ModelSingleton
from trytond.wizard import Wizard, StateAction, StateView, Button
from trytond.transaction import Transaction

__all__ = ['CEOReport', 'GenerateCEOReport', 'GenerateCEOReportStart']


class CEOReport(ReportWebkit):
    __name__ = 'ceo.report'

    @classmethod
    def wkhtml_to_pdf(cls, data, options=None):
        """
        Call wkhtmltopdf to convert the html to pdf
        """
        Company = Pool().get('company.company')

        company = ''
        if Transaction().context.get('company'):
            company = Company(Transaction().context.get('company')).party.name
        options = {
            'margin-bottom': '0.50in',
            'margin-left': '0.50in',
            'margin-right': '0.50in',
            'margin-top': '0.50in',
            'footer-font-size': '8',
            'footer-left': company,
            'footer-line': '',
            'footer-right': '[page]/[toPage]',
            'footer-spacing': '5',
        }
        return super(CEOReport, cls).wkhtml_to_pdf(
            data, options=options
        )

    @classmethod
    def parse(cls, report, records, data, localcontext):
        Sale = Pool().get('sale.sale')
        ShipmentOut = Pool().get('stock.shipment.out')
        Inventory = Pool().get('stock.inventory')
        Production = Pool().get('production')

        days = data['days']

        if data['sales']:
            sales = Sale.search([
                ('state', 'in', ['confirmed', 'processing', 'done']),
                ('write_date', '>=', (datetime.today() - relativedelta(days=days))),
            ])
            localcontext.update({
                'sales': sales,
            })
        if data['shipments']:
            shipments = ShipmentOut.search([
                ('state', 'in', ['done', 'packed', 'assigned', 'waiting']),
                ('write_date', '>=', (datetime.today() - relativedelta(days=days))),
            ])
            done_shipments_today = ShipmentOut.search([
                ('effective_date', '>=', (date.today() - relativedelta(days=days))),
                ('state', '=', 'done'),
            ], count=True)
            localcontext.update({
                'shipments': shipments,
                'done_shipments_today': done_shipments_today,
            })
        if data['productions']:
            productions = Production.search([
                ('state', 'in', ['done', 'running', 'assigned', 'waiting']),
                ('write_date', '>=', (datetime.today() - relativedelta(days=days))),
            ])
            localcontext.update({
                'productions': productions,
            })
        if data['inventories']:
            inventories = Inventory.search([
                ('date', '>=', (date.today() - relativedelta(days=days))),
            ])
            localcontext.update({
                'inventories': inventories,
            })
        return super(CEOReport, cls).parse(
            report, records, data, localcontext
        )


class GenerateCEOReportStart(ModelView):
    'Generate CEO Report'
    __name__ = 'ceo.report.generate.start'

    days = fields.Integer('No. of Days')
    sales = fields.Boolean('Sales')
    shipments = fields.Boolean('Shipments')
    productions = fields.Boolean('Productions')
    inventories = fields.Boolean('Inventories')

    @staticmethod
    def default_days():
        """
        Set default number of days as the days set in congifuration
        """
        CEOReportConfig = Pool().get('ceo.report.configuration')
        return CEOReportConfig(1).days

    @staticmethod
    def default_sales():
        """
        Set default from configuration
        """
        CEOReportConfig = Pool().get('ceo.report.configuration')
        return CEOReportConfig(1).sales

    @staticmethod
    def default_shipments():
        """
        Set default from configuration
        """
        CEOReportConfig = Pool().get('ceo.report.configuration')
        return CEOReportConfig(1).shipments

    @staticmethod
    def default_productions():
        """
        Set default from configuration
        """
        CEOReportConfig = Pool().get('ceo.report.configuration')
        return CEOReportConfig(1).productions

    @staticmethod
    def default_inventories():
        """
        Set default from configuration
        """
        CEOReportConfig = Pool().get('ceo.report.configuration')
        return CEOReportConfig(1).inventories


class GenerateCEOReport(Wizard):
    'Generate CEO Report Wizard'
    __name__ = 'ceo.report.generate'

    start = StateView(
        'ceo.report.generate.start',
        'ceo_report.ceo_report_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Ok', 'generate', 'tryton-ok', default=True),
        ]
    )
    generate = StateAction('ceo_report.ceo_report')

    def do_generate(self, action):
        """
        Sends the selected shop and customer as report data
        """
        data = {
            'days': self.start.days or 1,
            'sales': self.start.sales,
            'shipments': self.start.shipments,
            'inventories': self.start.inventories,
            'productions': self.start.productions,
        }
        return action, data

    def transition_generate(self):
        return 'end'


class CEOReportConfiguration(ModelSingleton, ModelSQL, ModelView):
    """
    CEO Report Configuration
    """
    __name__ = 'ceo.report.configuration'

    sales = fields.Boolean('Sales')
    shipments = fields.Boolean('Shipments')
    productions = fields.Boolean('Productions')
    inventories = fields.Boolean('Inventories')
    days = fields.Integer('No. of Days')

    @staticmethod
    def default_days():
        """
        Set default number of days as 1
        """
        return 1

    @staticmethod
    def default_sales():
        return True

    @staticmethod
    def default_shipments():
        return True

    @staticmethod
    def default_productions():
        return True

    @staticmethod
    def default_inventories():
        return True
