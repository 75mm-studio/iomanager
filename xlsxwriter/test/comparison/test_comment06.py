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

        self.set_filename('comment06.xlsx')

    def test_create_file(self):
        """Test the creation of a simple XlsxWriter file with comments."""

        workbook = Workbook(self.got_filename)

        worksheet = workbook.add_worksheet()

        worksheet.write_comment('A1', 'Some text')
        worksheet.write_comment('A2', 'Some text')
        worksheet.write_comment('A3', 'Some text', {'visible': True})
        worksheet.write_comment('A4', 'Some text')
        worksheet.write_comment('A5', 'Some text')

        worksheet.set_comments_author('John')

        workbook.close()

        self.assertExcelEqual()
