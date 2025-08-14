from pathlib import Path
from typing import Union

import pandas as pd
from pywintypes import com_error
from win32com.client import DispatchEx

from hmcis_packs.clean.cleaner import DataframeCleaner
from hmcis_packs.logger.logger_config import setup_logger

logger = setup_logger(__name__)
# logger.setLevel(logging.INFO)

logger.propagate = False


class ExcelParser:
    """
    Reads an Excel sheet via a fresh COM instance, cleans it, and returns a DataFrame.

    Parameters:
      filepath: path to the .xlsx file
      sheet: worksheet to read
      index_value: row-label to use as index
      retain_duplicates: if False, will drop duplicate columns
      visible: if True, the Excel window pops up (default False)
    """

    def __init__(
            self,
            filepath: Union[str, Path],
            sheet: Union[str, int],
            index_value: str,
            *,
            retain_duplicates: bool = False,
            visible: bool = False,
    ) -> None:
        self.filepath = Path(filepath)
        self.sheet = sheet
        self.index_value = index_value
        self.retain_duplicates = retain_duplicates
        self.visible = visible

    def _new_excel_app(self):
        """Always launch a new Excel COM server."""
        try:
            app = DispatchEx("Excel.Application")
            app.Visible = self.visible
            logger.info("Launched new Excel instance (PID: %r)", app.Hwnd)
            return app
        except com_error as e:
            logger.exception("Failed to launch Excel: %s", e)
            raise

    def _resolve_sheet(self, wb):
        """
        Return a COM sheet object by index (1-based) or by (sub)name.
        Raises ValueError if not found or index is out of range.
        """
        if isinstance(self.sheet, int):
            # 1-based index as per Excel COM
            try:
                sht = wb.Sheets[self.sheet]
                logger.info("Resolved sheet by 1-based index: %s", sht.Name)
                return sht
            except com_error:
                raise ValueError(f"Sheet index {self.sheet} is out of range.")
        else:
            # substring match; take first match
            name_sub = str(self.sheet)
            matches = [sht for sht in wb.Sheets if name_sub in sht.Name]
            if not matches:
                raise ValueError(f"No sheet name containing '{name_sub}' found.")
            if len(matches) > 1:
                logger.warning(
                    "Multiple sheets matched '%s'; using the first: %s",
                    name_sub, matches[0].Name
                )
            logger.info("Resolved sheet by name: %s", matches[0].Name)
            return matches[0]

    def read_data(self) -> pd.DataFrame:
        app = self._new_excel_app()
        try:
            wb = app.Workbooks.Open(
                Filename=str(self.filepath),
                ReadOnly=True,
                UpdateLinks=False,
            )
            try:
                sheet = self._resolve_sheet(wb)
                logger.info(f'Processing data on the following sheet -->> {sheet.Name}')
                # sheet = wb.Sheets[self.sheet_name]
                raw = sheet.UsedRange.Value  # tuple-of-tuples
                df = pd.DataFrame(raw)
                cleaner = DataframeCleaner(df)
                cleaner.adj_by_row_index(self.index_value)

                if not self.retain_duplicates:
                    cleaner.remove_duplicated_cols()

                return cleaner.df
            finally:
                wb.Close(SaveChanges=False)
        finally:
            # make sure to quit Excel even if something goes wrong
            app.Quit()
            logger.info("Closed Excel instance.")


if __name__ == "__main__":
    parser = ExcelParser(
        r"V:\Accounting\Work\Мерц\2025\2 квартал 2025\Июнь 2025\Отчетность\!Начисление МСФО_июнь 2025.xlsx",
        sheet=3,
        index_value="Отдел инициатор",
        retain_duplicates=False,
        visible=True,  # only if you want Excel to pop up
    )
    df = parser.read_data()
    print(df)
