###############################################################################
#
# Tests for XlsxWriter.
#
# Copyright (c), 2013-2019, John McNamara, jmcnamara@cpan.org
#

from ..excel_comparsion_test import ExcelComparisonTest
from ...workbook import Workbook


class TestCompareXLSXFiles(ExcelComparisonTest):
    """
    Test file created by XlsxWriter against a file created by Excel.

    """

    def setUp(self):

        self.set_filename('cond_format20.xlsx')

    def test_create_file(self):
        """Test the creation of a simple XlsxWriter file with conditionalformatting."""

        workbook = Workbook(self.got_filename)

        worksheet = workbook.add_worksheet()

        worksheet.write('A1', 10)
        worksheet.write('A2', 20)
        worksheet.write('A3', 30)
        worksheet.write('A4', 40)

        worksheet.conditional_format('A1:A4',
                                     {'type': 'icon_set',
                                      'icon_style': '3_arrows',
                                      'icons': [{'criteria': '>', 'type': 'percent', 'value': 0},
                                                {'criteria': '<', 'type': 'percent', 'value': 0},
                                                {'criteria': '>=', 'type': 'percent', 'value': 0}]})

        workbook.close()

        self.assertExcelEqual()
