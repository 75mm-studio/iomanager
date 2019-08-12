###############################################################################
#
# Tests for XlsxWriter.
#
# Copyright (c), 2013-2019, John McNamara, jmcnamara@cpan.org
#

from ..excel_comparsion_test import ExcelComparisonTest
from ...workbook import Workbook
from io import BytesIO


class TestCompareXLSXFiles(ExcelComparisonTest):
    """
    Test file created by XlsxWriter against a file created by Excel.

    """

    def setUp(self):

        self.set_filename('macro02.xlsm')

    def test_create_file(self):
        """Test the creation of a simple XlsxWriter file."""

        workbook = Workbook(self.got_filename)

        worksheet = workbook.add_worksheet()

        workbook.add_vba_project(self.vba_dir + 'vbaProject03.bin')
        workbook.set_vba_name('MyWorkbook')
        worksheet.set_vba_name('MySheet1')

        worksheet.write('A1', 123)

        workbook.close()

        self.assertExcelEqual()
