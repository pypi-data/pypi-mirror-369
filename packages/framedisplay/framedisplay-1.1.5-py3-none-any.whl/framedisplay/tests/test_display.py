import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from framedisplay import dataframe_to_html


class TestDataframeToHtml:
    def test_basic_dataframe(self):
        """Test basic dataframe conversion to HTML."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})

        html = dataframe_to_html(df)
        soup = BeautifulSoup(html, "html.parser")

        # Check table structure
        assert soup.find("table", class_="frame-display-table") is not None

        # Check headers
        headers = soup.find("thead").find_all("th")
        assert len(headers) == 3  # Index + 2 columns
        assert headers[1].text == "A"
        assert headers[2].text == "B"

        # Check data rows
        rows = soup.find("tbody").find_all("tr")
        assert len(rows) == 3

    def test_null_values(self):
        """Test null value handling with null-cell class."""
        df = pd.DataFrame({"A": [1, np.nan, 3], "B": ["x", np.nan, "z"]})

        html = dataframe_to_html(df)
        soup = BeautifulSoup(html, "html.parser")

        # Find code elements with null-cell class (what your function actually does)
        null_elements = soup.find_all("code", class_="null-cell")
        assert len(null_elements) == 2

        # Check null element content
        for element in null_elements:
            assert element.text == "null"

        # Verify they're inside td elements
        for element in null_elements:
            assert element.parent.name == "td"

    def test_html_escaping(self):
        """Test that HTML characters are properly escaped."""
        df = pd.DataFrame({"A": ["<script>", "&amp;", '"quotes"']})

        html = dataframe_to_html(df)

        # Should not contain unescaped HTML
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
        assert "&amp;amp;" in html
        assert "&quot;quotes&quot;" in html

    def test_empty_dataframe(self):
        """Test empty dataframe handling."""
        df = pd.DataFrame()

        html = dataframe_to_html(df)
        soup = BeautifulSoup(html, "html.parser")

        # Should still have table structure
        assert soup.find("table", class_="frame-display-table") is not None
        assert soup.find("thead") is not None
        assert soup.find("tbody") is not None

    def test_single_row_dataframe(self):
        """Test single row dataframe."""
        df = pd.DataFrame({"A": [1], "B": ["test"]})

        html = dataframe_to_html(df)
        soup = BeautifulSoup(html, "html.parser")

        rows = soup.find("tbody").find_all("tr")
        assert len(rows) == 1

        cells = rows[0].find_all(["th", "td"])
        assert len(cells) == 3  # Index + 2 data columns

    def test_mixed_data_types(self):
        """Test dataframe with mixed data types."""
        df = pd.DataFrame(
            {
                "int_col": [1, 2, 3],
                "float_col": [1.1, 2.2, 3.3],
                "str_col": ["a", "b", "c"],
                "bool_col": [True, False, True],
            }
        )

        html = dataframe_to_html(df)
        soup = BeautifulSoup(html, "html.parser")

        # Check all columns are present
        headers = soup.find("thead").find_all("th")
        assert len(headers) == 5  # Index + 4 columns

        # Check data is properly converted to strings
        rows = soup.find("tbody").find_all("tr")
        assert len(rows) == 3

    def test_index_handling(self):
        """Test that index values are properly displayed."""
        df = pd.DataFrame({"A": [1, 2]}, index=["row1", "row2"])

        html = dataframe_to_html(df)
        soup = BeautifulSoup(html, "html.parser")

        # Check index cells (first th in each row)
        rows = soup.find("tbody").find_all("tr")
        index_cells = [row.find("th") for row in rows]

        assert index_cells[0].text == "row1"
        assert index_cells[1].text == "row2"
