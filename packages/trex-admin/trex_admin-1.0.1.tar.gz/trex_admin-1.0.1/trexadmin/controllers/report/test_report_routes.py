'''
Created on 8 Jan 2021

@author: jacklok
'''
from flask import Blueprint, render_template, request, Response
from trexadmin.libs.flask.utils.flask_helper import output_html
from flask_restful import Resource, Api
import logging

test_report_bp = Blueprint('test_report_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/report/test')


logger = logging.getLogger('report')

test_report = Api(test_report_bp)



class TestReportIndex(Resource):
    def get(self):
        content = render_template('report/test_report_index.html')
        return output_html(content)
    

class StackedChart1(Resource):
    def get(self):
        content = render_template('report/test/stacked_chart_1.html')
        return output_html(content)


test_report.add_resource(TestReportIndex, '/')
test_report.add_resource(StackedChart1, '/stacked1')