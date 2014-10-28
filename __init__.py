# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from ceo_report import CEOReport, GenerateCEOReport, GenerateCEOReportStart, \
    CEOReportConfiguration


def register():
    Pool.register(
        GenerateCEOReportStart,
        CEOReportConfiguration,
        module='ceo_report', type_='model'
    )
    Pool.register(
        CEOReport,
        module='ceo_report', type_='report'
    )
    Pool.register(
        GenerateCEOReport,
        module='ceo_report', type_='wizard'
    )
