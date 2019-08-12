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

        self.set_filename('rich_string06.xlsx')

    def test_create_file(self):
        """Test the creation of a simple XlsxWriter file."""

        workbook = Workbook(self.got_filename)

        worksheet = workbook.add_worksheet()

        red = workbook.add_format({'color': 'red'})

        worksheet.write('A1', 'Foo', red)
        worksheet.write('A2', 'Bar')
        worksheet.write_rich_string('A3', 'ab', red, 'cde', 'fg')

        workbook.close()

        self.assertExcelEqual()
