#!/usr/bin/env python3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .cyberark import Cyberark
from gspread.exceptions import WorksheetNotFound

class UMGoogleSheet(object):
    def __init__(self, ss):
        cyberark = Cyberark("UMNET")
        self.scope_app = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.service_account_email = str(cyberark.query_cyberark("gsheet_api_service_account_email"))
        self.project_id = str(cyberark.query_cyberark("gsheet_api_project_id"))
        self.client_id = str(cyberark.query_cyberark("gsheet_api_client_id"))
        self.private_key_id = str(cyberark.query_cyberark("gsheet_api_key_id"))
        self.private_key = str(cyberark.query_cyberark("gsheet_api_private_key")).replace("\\n", "\n")

        self.open_spreadsheet(ss)

    def _col_to_a1(col_num:int)->str:
        """
        Converts a column number to A1 notation.
        """

    def _gsheet_auth(self):
        json_creds = {
            "type": "service_account",
            "project_id": self.project_id,
            "private_key_id": self.private_key_id,
            "private_key": self.private_key,
            "client_email": self.service_account_email,
            "client_id": self.client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/" + self.service_account_email.replace("@", "%40"),
        }
        cred = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, self.scope_app)

        # authorize the clientsheet
        return gspread.authorize(cred)


    def open_spreadsheet(self, url_or_key):
        '''
        Opens a spreadsheet by url or by key. Detects a url by looking for 'https'
        '''
        self._client = self._gsheet_auth()
        if url_or_key.startswith('http'):
            self._ss = self._client.open_by_url(url_or_key)
        else:
            self._ss = self._client.open_by_key(url_or_key)

    def get_worksheet(self, ws_name):
        '''
        Gets a worksheet by name. If return as dict is set to true (default is yet),
        will return the results of "get all records". Otherwise will return a worksheet object.
        '''
        return self._ss.worksheet(ws_name)

    def get_worksheet_values(self, ws_name, numericise_ignore=[]):
        """
        numericise_ignore (list) – (optional) List of ints of indices of the
        columns (starting at 1) to ignore numericising, special use of [‘all’]
        to ignore numericising on all columns.
        """
        ws = self.get_worksheet(ws_name)
        return ws.get_all_records(numericise_ignore=numericise_ignore)

    def open_and_get_worksheet(self, url_or_key, ws_name):
        """
        Opens a spreadsheet and gets a worksheet by name from that spreadsheet.
        """
        self.open_spreadsheet(url_or_key)
        return self.get_worksheet(ws_name, return_as_dict=True)

    def open_and_get_worksheet_values(self, url_or_key, ws_name, numericise_ignore=[]):
        """
        numericise_ignore (list) – (optional) List of ints of indices of the
        columns (starting at 1) to ignore numericising, special use of [‘all’]
        to ignore numericising on all columns.
        """
        ws = self.open_and_get_worksheet(url_or_key, ws_name)
        return ws.get_all_records(numericise_ignore=numericise_ignore)

    def find_row_in_worksheet(self, ws_name, search_term, as_dict=True):
        """
        Finds the first row on a specific worksheet where the search term
        matches a cell in that row. If it is found, will either
        return as a dict with header (row 1) as the keys, or as a simple list
        """
        ws = self._ss.worksheet(ws_name)
        cell = ws.find(search_term)
        if cell:
            row = ws.row_values(cell.row)
            if as_dict:
                headers = ws.row_values(1)
                return {headers[i]:row[i] for i in range(0,len(row)-1)}
            else:
                return row
        else:
            return None


    def find_rows_in_worksheet(self, ws_name, search_term, as_dict=True):
        """
        Finds ALL rows on a specific worksheet where the search term
        matches a cell in that row. If it is found, will either
        return as a list of dicts with header (row 1) as the keys, or as a list of lists
        """
        ws = self._ss.worksheet(ws_name)
        cells = ws.findall(search_term)
        results = []
        for cell in cells:
            row = ws.row_values(cell.row)
            if as_dict:
                headers = ws.row_values(1)
                [row.append("") for x in range(0,len(headers)-len(row))]
                results.append({headers[i]:row[i] for i in range(0,len(headers))})
            else:
                results.append(row)
       
        return results
    
    def create_or_overwrite_worksheet(self, ws_name, data:list):
        """
        Creates a new worksheet or overwrites an existing one
        with the data provided.

        If the data is a dictionary, the keys become a header for row 1
        Otherwise data is assumed to be a list of lists of all the same
        length (letting gspreads api validate that)
        """

        if isinstance(data[0], dict):
            ws_data = []
            ws_data.append(list(data[0].keys()))
            [ ws_data.append(list(row.values())) for row in data ]
        elif isinstance(data[0], list):
            ws_data = data
        else:
            raise TypeError(f'Data must be a list of dicts or list of lists')
        
        num_rows = len(ws_data)
        num_cols = len(ws_data[0])

        # each row might have a different number of columns - we need to
        # find the longest row to figure out the size of our update
        for row in ws_data:
            if len(row) > num_cols:
                num_cols = len(row)

        try:
            ws = self._ss.worksheet(ws_name)
            ws.clear()
        except WorksheetNotFound:
            ws = self._ss.add_worksheet(ws_name, num_rows, num_cols)
        
        last_cell = gspread.utils.rowcol_to_a1(num_rows, num_cols)
        ws.update(f'A1:{last_cell}', ws_data)


    def diff_worksheets(self, ws1_name, ws2_name):
        """
        Compares the data on two worksheets. Rows that don't match are
        highlighted on both sheets
        """
        ws1 = self._ss.worksheet(ws1_name)
        ws2 = self._ss.worksheet(ws2_name)

        ws1_vals = ws1.get_values()
        ws2_vals = ws2.get_values()

        diff_cells = []
        for row1, row2, row_num in zip(ws1_vals, ws2_vals, range(1,len(ws1_vals))):
            for col1, col2, col_num in zip(row1, row2, range(1,len(row1))):
                if col1 != col2:
                    diff_cells.append((row_num, col_num))

        if diff_cells:
            formats = [
                { 
                    "range": gspread.utils.rowcol_to_a1(c[0], c[1]),
                    "format": {
                        "backgroundColor": {
                            "red": 1.0,
                            "green": 0.0,
                            "blue": 0.0,
                        }
                    }
                }

                for c in diff_cells
            ]
            ws1.batch_format(formats)
            ws2.batch_format(formats)
    
    def diff_worksheet_rows(self, ws1_name, ws2_name, col_key_idx=1):
        """
        Compares the data on two worksheets but ignores row order - it is assumed that
        the columns on both sheets are the same and we want those to match.

        You must provide a column index that allows us to uniquely identify each row.
        IMPORTANT: ** Column indexes must be provided as integers (not letters) and start at 1 **
        That index is used to map rows on sheet 1 to rows on sheet 2. Once a mapping is found
        that row on sheet 1 is compared to the same row on sheet 2 and vice versa.
        """

        ws1 = self._ss.worksheet(ws1_name)
        ws2 = self._ss.worksheet(ws2_name)

        ws1_vals = ws1.get_values()
        ws2_vals = ws2.get_values()

        # making sure our index is within bounds and our spreadsheets have the same number of columns
        if col_key_idx >= len(ws1_vals[0]):
            raise ValueError(f"Column key index {col_key_idx} is out of bounds!")
        if len(ws1_vals[0]) != len(ws2_vals[0]):
            raise ValueError(f"{ws1_name} and {ws2_name} don't have the same number of columns!")
        
        # blow away existing foramtting
        self.clear_text_and_background_colors(ws1)
        self.clear_text_and_background_colors(ws2)

        # compare 1 to 2 and 2 to 1
        self._rows_compare(ws1, ws1_vals, ws2_vals, col_key_idx)
        self._rows_compare(ws2, ws2_vals, ws1_vals, col_key_idx)

    
    def _rows_compare(self, ws1, ws1_vals, ws2_vals, col_key_idx):
        """
        Workhorse of the rows compare - compares ws1 to ws2 and updates the formats on ws1
        where discrepancies are found
        """
        diff_cells = []
    
        # had issues using the 'range' keyword in this function, no idea why. Instead of
        # figuring it out I've decided to just use old school index counters.
        row_idx = 1 
        for ws1_row in ws1_vals:

            found_match = False

            for ws2_row in ws2_vals:

                # if the data in the key column for this ws1 row matches one in ws2,
                # we've found a match
                if ws1_row[col_key_idx-1] == ws2_row[col_key_idx-1]:
                    found_match = True

                    # if there's a discrepancy in any of the other columns on these two rows
                    # mark them to be reddened
                    col_idx = 1
                    for ws1_col, ws2_col in zip(ws1_row, ws2_row):
                        if ws1_col != ws2_col:
                            diff_cells.append((row_idx, col_idx))
                        col_idx += 1               
                    continue
            
            # if we didn't find a row in ws2 that matches ws1, redden the whole ws1 row
            if not(found_match):
                diff_cells.append(row_idx)

            row_idx += 1

        # redden the discrepancies with a batch format update
        if diff_cells:
            formats = []
            for c in diff_cells:

                # if some cells on this row are different than the other row, turn the text red
                if isinstance(c, tuple):
                    range = gspread.utils.rowcol_to_a1(c[0], c[1])
                    formats.append(
                    { 
                        "range": range,
                        "format": {
                            "textFormat": {
                                "foregroundColor": {"red": 1.0, "green": 0.0, "blue": 0.0}
                            }
                        }
                    })

                # if a whole row is missing, turn the background red                  
                else:
                    range = f'A{c}:{gspread.utils.rowcol_to_a1(c, len(ws1_row))}'
                    formats.append(
                    { 
                        "range": range,
                        "format": {
                            "backgroundColor": {"red": 1.0, "green": 0.0, "blue": 0.0}
                        }
                    })
            
            ws1.batch_format(formats)

    def clear_text_and_background_colors(self, ws, a1_range=None):
        """
        Clears the text color and background colors (sets text to black and background to white)
        tbd: figure out how to clear all formatting. You'd think they'd have a way to  
        """
        if a1_range:
            range = a1_range
        else:
            last_cell = gspread.utils.rowcol_to_a1(ws.row_count, ws.col_count)
            range = f'A1:{last_cell}'

        ws.format(range,
                {
                    "textFormat": {
                        "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0}
                        },
                    "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                }
                   
        )