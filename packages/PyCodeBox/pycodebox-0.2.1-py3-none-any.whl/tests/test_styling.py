import pandas as pd
from pycodebox.styling import (
  export_styled_xlsx_w_2_headers,
  display_styled_table_w_2_headers,
)


def test_export_styled_xlsx(tmp_path):
  df = pd.DataFrame([['Header1', 'Header2'], ['Sub1', 'Sub2'], [1, 2]])
  filename = tmp_path / 'test.xlsx'
  export_styled_xlsx_w_2_headers(df, 'TestSheet', str(filename))
  assert filename.exists()


def test_display_styled_table_w_2_headers():
  df = pd.DataFrame([['Header1', 'Header2'], ['Sub1', 'Sub2'], [1, 2]])
  display_styled_table_w_2_headers(df, rows_per_page=20)
  assert True  # Just checking it runs without error
