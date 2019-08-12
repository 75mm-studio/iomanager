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

        self.set_filename('default_row02.xlsx')

    def test_create_file(self):
        """Test the creation of a simple XlsxWriter file."""

        workbook = Workbook(self.got_filename)

        worksheet = workbook.add_worksheet()

        worksheet.set_default_row(hide_unused_rows=True)

        worksheet.write('A1', 'Foo')
        worksheet.write('A10', 'Bar')

        for row in range(1, 8 + 1):
            worksheet.set_row(row, 15)

        workbook.close()

        self.assertExcelEqual()
