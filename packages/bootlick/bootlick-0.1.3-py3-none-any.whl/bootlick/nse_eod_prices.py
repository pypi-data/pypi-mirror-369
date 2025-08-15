import datetime as dt
import io
import logging
import os
import traceback

import numpy as np
import pandas as pd
from chameli.dateutils import valid_datetime
from chameli.interactions import (
    file_exists_and_valid,
    list_directory,
    make_directory,
    read_csv_from_zip,
    read_csv_in_pandas_out,
    readRDS,
    save_file,
    save_pandas_in_csv_out,
    saveRDS,
    send_mail,
)
from ohlcutils.data import _split_adjust_market_data, get_linked_symbols
from ohlcutils.enums import Periodicity

from .config import get_config


# Import bootlick_logger lazily to avoid circular import
def get_bootlick_logger():
    """Get bootlick_logger instance to avoid circular imports."""
    from . import bootlick_logger

    return bootlick_logger


def get_dynamic_config():
    return get_config()


def catch(func, *args, handle=lambda e: e, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return handle(e)


def check_float(potential_float):
    try:
        return float(potential_float)
    except ValueError:
        return potential_float


def get_first_day_of_the_quarter(p_date: dt.date):
    currQuarter = (p_date.month - 1) // 3 + 1
    return dt.datetime(p_date.year, 3 * currQuarter - 2, 1)


def save_equity_data(p: str, session, save_to_rds=True):
    """Save Equity Data to Folder

    Args:
        p (str): processing date as YYYYMMDD
        session: HTTP session for making requests
    """

    def update_symbol(filename_to_update, filename_to_save, row):
        try:
            md = readRDS(filename_to_update)
            md["date"] = md["date"].dt.tz_localize("UTC")
            md["date"] = md["date"].dt.tz_convert("Asia/Kolkata")
        except Exception as e:
            get_bootlick_logger().log_warning(
                f"Failed to read RDS file {filename_to_update}: {e}",
                {"filename_to_update": filename_to_update, "error_type": type(e).__name__, "error_message": str(e)},
            )
            md = pd.DataFrame()
        md_updated = pd.concat([md, row], ignore_index=True)
        md_updated = md_updated.drop_duplicates(subset="date", keep="last")
        md_updated = md_updated.sort_values(by="date")
        md_updated.symbol = md_updated.symbol.iloc[0]
        if "splitadjust" in md_updated.columns:
            md_updated.drop("splitadjust", axis=1, inplace=True)
        md_updated = md_updated[~md_updated.date.duplicated(keep="last")]
        if "tradecount" in md_updated.columns:
            md_updated["tradecount"] = md_updated["tradecount"].fillna(-1).astype(int)
        md_updated.set_index("date", inplace=True)
        md_updated = _split_adjust_market_data(md_updated, src=Periodicity.DAILY, tz="Asia/Kolkata")
        md_updated.reset_index(inplace=True)
        saveRDS(md_updated, filename_to_save)

    try:
        outfolder = f"{get_dynamic_config().get('daily_prices')}/stk"
        url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{valid_datetime(p,'%d%m%Y')[0]}.csv"
        dest_file = f"{get_dynamic_config().get('bhavcopy_folder')}/{p}_equity.csv"

        # Check if destination file exists
        if file_exists_and_valid(dest_file, min_size=1000):
            get_bootlick_logger().log_info(f"File already exists: {dest_file}", {"dest_file": dest_file})
            if not save_to_rds:
                return
            data = read_csv_in_pandas_out(dest_file, dtype=str)
        else:
            # Downloading the file
            response = session.get(url)
            if response.status_code == 200:
                save_file(dest_file, response.content)
                get_bootlick_logger().log_info(
                    f"Equity bhavcopy downloaded and saved successfully for {p}", {"date": p, "file_type": "equity"}
                )
                if not save_to_rds:
                    return
                data = read_csv_in_pandas_out(dest_file, dtype=str)
            else:
                get_bootlick_logger().log_error(
                    f"Failed to download equity file for {p}. Status code: {response.status_code}",
                    None,
                    {"date": p, "status_code": response.status_code, "file_type": "equity"},
                )
                send_mail(
                    get_dynamic_config().get("from_email_id"),
                    get_dynamic_config().get("to_email_id"),
                    get_dynamic_config().get("from_email_password"),
                    f"Unable to download equity file for {p}",
                    f"HTTP Status Code: {response.status_code}",
                )
                return

        if file_exists_and_valid(dest_file, min_size=1000):
            # Reading the CSV file
            data.columns = [col.strip() for col in data.columns]
            data = data.map(lambda x: x.strip() if isinstance(x, str) else x)
            data = data[data["SERIES"].isin(["EQ", "BZ", "BE", "IV", "RR"])]

            # Converting 'DATE1' to datetime and adjusting timezone
            data["TIMESTAMP"] = pd.to_datetime(data["DATE1"], format="%d-%b-%Y").dt.tz_localize("Asia/Kolkata")

            # Renaming 'NO_OF_TRADES' to 'TOTALTRADES'
            data.loc[:, "TOTALTRADES"] = data["NO_OF_TRADES"]

            # Trimming whitespace and converting 'DELIV_QTY' to numeric, replacing NaNs with 0
            data.loc[:, "DELIV_QTY"] = data["DELIV_QTY"].str.strip()
            data.loc[:, "DELIV_QTY"] = pd.to_numeric(data["DELIV_QTY"], errors="coerce").fillna(0)
            data.loc[:, "TURNOVER_LACS"] = pd.to_numeric(data["TURNOVER_LACS"], errors="coerce").fillna(0)

            # Converting specific columns to numeric
            numeric_columns = [
                "OPEN_PRICE",
                "HIGH_PRICE",
                "LOW_PRICE",
                "LAST_PRICE",
                "CLOSE_PRICE",
                "TTL_TRD_QNTY",
                "NO_OF_TRADES",
                "DELIV_QTY",
                "TURNOVER_LACS",
            ]
            for col in numeric_columns:
                data[col] = pd.to_numeric(data[col], errors="coerce")

            # Process each row in the data
            for i in range(len(data)):
                d = data.iloc[i]
                symbol = f"{d['SYMBOL']}_STK___"
                get_bootlick_logger().log_info(f"Processing Daily Bars for {symbol}", {"symbol": symbol})
                df = pd.DataFrame(
                    {
                        "date": pd.to_datetime(d["TIMESTAMP"]),
                        "open": d["OPEN_PRICE"],
                        "high": d["HIGH_PRICE"],
                        "low": d["LOW_PRICE"],
                        "close": d["LAST_PRICE"],
                        "settle": d["CLOSE_PRICE"],
                        "volume": d["TTL_TRD_QNTY"],
                        "tradecount": d["NO_OF_TRADES"],
                        "delivered": d["DELIV_QTY"],
                        "tradedvalue": d["TURNOVER_LACS"] * 100000,
                        "symbol": symbol,
                    },
                    index=[0],
                )
                filename = os.path.join(outfolder, f"{symbol}.rds")
                if file_exists_and_valid(filename, min_size=1):
                    update_symbol(filename, filename, df)
                    potential_link = get_linked_symbols(df.symbol.item())
                    if len(potential_link) > 1:
                        current_link_index = np.where(d.symbol == potential_link.symbol)[0][0]
                        if current_link_index > 0:  # we have name change[s]. merge current data into new name[s]
                            potential_link = potential_link[0:current_link_index]
                            for new_symbol in potential_link.symbol:
                                new_symbol = f"{outfolder}/{new_symbol}_STK___.rds"
                                update_symbol(new_symbol, new_symbol, df)
                else:
                    potential_link = get_linked_symbols(df.symbol.item())
                    if len(potential_link) > 1:
                        current_link_index = np.where(d.symbol == potential_link.symbol)[0][0]
                        for new_symbol in potential_link.symbol[current_link_index:][::-1]:
                            new_symbol = f"{outfolder}/{new_symbol}_STK___.rds"
                            filename_to_save = f"{outfolder}/{df.symbol[0]}.rds"
                            update_symbol(new_symbol, filename_to_save, df)
                    else:
                        filename_to_save = f"{outfolder}/{df.symbol[0]}.rds"
                        update_symbol(filename_to_save, filename_to_save, df)
    except Exception as e:
        get_bootlick_logger().log_error(f"Error in save_equity_data", e, {"function": "save_equity_data"})
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Unable to process equity data for {p}",
            f"{traceback.format_exc()}",
        )


def save_index_data(p: str, session, save_to_rds=True):
    """Save Index Data to Folder

    Args:
        p (str): processing date as YYYYMMDD
        session: HTTP session for making requests
    """

    def update_symbol(filename_to_update, filename_to_save, row):
        """Update the RDS file with new data."""
        try:
            md = readRDS(filename_to_update)
            md["date"] = md["date"].dt.tz_localize("UTC")
            md["date"] = md["date"].dt.tz_convert("Asia/Kolkata")
        except Exception as e:
            get_bootlick_logger().log_warning(
                f"Failed to read RDS file {filename_to_update}: {e}",
                {"filename_to_update": filename_to_update, "error_type": type(e).__name__, "error_message": str(e)},
            )
            md = pd.DataFrame()
        md_updated = pd.concat([md, row], ignore_index=True)
        md_updated = md_updated.drop_duplicates(subset="date", keep="last")
        md_updated = md_updated.sort_values(by="date")
        md_updated.symbol = md_updated.symbol.iloc[0]
        saveRDS(md_updated, filename_to_save)

    try:
        outfolder = f"{get_dynamic_config().get('daily_prices')}/ind"
        url = f"https://archives.nseindia.com/content/indices/ind_close_all_{valid_datetime(p,'%d%m%Y')[0]}.csv"
        # alternative https://www.niftyindices.com/Daily_Snapshot/ind_close_all_06082025.csv
        dest_file = f"{get_dynamic_config().get('bhavcopy_folder')}/{p}_index.csv"

        # Check if destination file exists
        if file_exists_and_valid(dest_file, min_size=1000):
            get_bootlick_logger().log_info(f"File already exists: {dest_file}", {"dest_file": dest_file})
            if not save_to_rds:
                return
            data = read_csv_in_pandas_out(dest_file, dtype=str)
        else:
            # Downloading the file
            response = session.get(url)
            if response.status_code == 200:
                save_file(dest_file, response.content)
                get_bootlick_logger().log_info(
                    f"Index bhavcopy downloaded and saved successfully for {p}", {"date": p, "file_type": "index"}
                )
                if not save_to_rds:
                    return
                data = read_csv_in_pandas_out(dest_file, dtype=str)
            else:
                get_bootlick_logger().log_error(
                    f"Failed to download index file for {p}. Status code: {response.status_code}",
                    None,
                    {"date": p, "status_code": response.status_code, "file_type": "index"},
                )
                send_mail(
                    get_dynamic_config().get("from_email_id"),
                    get_dynamic_config().get("to_email_id"),
                    get_dynamic_config().get("from_email_password"),
                    f"Unable to download index file for {p}",
                    f"HTTP Status Code: {response.status_code}",
                )
                return

        if file_exists_and_valid(dest_file, min_size=1000):
            # Reading the CSV file
            data.columns = [col.strip() for col in data.columns]
            data = data.map(lambda x: x.strip() if isinstance(x, str) else x)

            # Converting 'Index Date' to datetime and setting timezone
            data["TIMESTAMP"] = pd.to_datetime(data["Index Date"], format="%d-%m-%Y")
            data["TIMESTAMP"] = data["TIMESTAMP"].dt.tz_localize("Asia/Kolkata")

            # Cleaning and transforming 'Index Name'
            data["SYMBOL"] = data["Index Name"].str.replace(" ", "", regex=False).str.upper()

            # Replacing specific patterns in 'SYMBOL'
            replacements = {
                r"^NIFTY50$": "NSENIFTY",
                r"^CNXNIFTY$": "NSENIFTY",
                r"^NIFTYBANK$": "BANKNIFTY",
                r"^CNXBANK$": "BANKNIFTY",
                r"^NIFTYFINANCIALSERVICES$": "FINNIFTY",
            }
            for pattern, replacement in replacements.items():
                data.loc[data["SYMBOL"].str.match(pattern), "SYMBOL"] = replacement

            # Removing slashes and appending "_IND___"
            data["SYMBOL"] = data["SYMBOL"].str.replace("/", "", regex=False) + "_IND___"

            # Converting specific columns to numeric
            numeric_columns = [
                "Open Index Value",
                "High Index Value",
                "Low Index Value",
                "Closing Index Value",
                "Volume",
                "P/E",
                "P/B",
                "Div Yield",
                "Turnover (Rs. Cr.)",
            ]
            for col in numeric_columns:
                data[col] = pd.to_numeric(data[col], errors="coerce")

            # Process each row in the data
            for i in range(len(data)):
                d = data.iloc[i]
                df = pd.DataFrame(
                    {
                        "date": [d["TIMESTAMP"]],
                        "open": [d["Open Index Value"]],
                        "high": [d["High Index Value"]],
                        "low": [d["Low Index Value"]],
                        "close": [d["Closing Index Value"]],
                        "settle": [d["Closing Index Value"]],
                        "volume": [d["Volume"]],
                        "tradedvalue": [d["Turnover (Rs. Cr.)"]],
                        "pe": [d["P/E"]],
                        "pb": [d["P/B"]],
                        "dividendyield": [d["Div Yield"]],
                        "symbol": [d["SYMBOL"]],
                    }
                )

                # Construct the filename
                filename = os.path.join(outfolder, f"{d['SYMBOL']}.rds")
                get_bootlick_logger().log_info(f"Processing Daily Bars for {d['SYMBOL']}", {"symbol": d["SYMBOL"]})

                if file_exists_and_valid(filename, min_size=1):
                    update_symbol(filename, filename, df)
                    potential_link = get_linked_symbols(df.symbol.item())
                    if len(potential_link) > 1:
                        current_link_index = np.where(d["SYMBOL"] == potential_link.symbol)[0][0]
                        if current_link_index > 0:  # we have name change[s]. merge current data into new name[s]
                            potential_link = potential_link[0:current_link_index]
                            for new_symbol in potential_link.symbol:
                                new_symbol = f"{outfolder}/{new_symbol}_IND___.rds"
                                update_symbol(new_symbol, new_symbol, df)
                else:
                    potential_link = get_linked_symbols(df.symbol.item())
                    if len(potential_link) > 1:
                        current_link_index = np.where(d.symbol == potential_link.symbol)[0][0]
                        for new_symbol in potential_link.symbol[current_link_index:][::-1]:
                            new_symbol = f"{outfolder}/{new_symbol}_IND___.rds"
                            filename_to_save = f"{outfolder}/{df.symbol[0]}_IND___.rds"
                            update_symbol(new_symbol, filename_to_save, df)
                    else:
                        filename_to_save = f"{outfolder}/{df.symbol[0]}_IND___.rds"
                        update_symbol(filename_to_save, filename_to_save, df)

    except Exception as e:
        get_bootlick_logger().log_error(f"Error in save_index_data", e, {"function": "save_index_data"})
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Unable to process index data for {p}",
            f"{traceback.format_exc()}",
        )


def save_future_data_old(p: str, session):
    """Save Future Data to Folder (Supported till and including 20240705)

    Args:
        p (str): Processing date as YYYYMMDD
        session: HTTP session for making requests
    """

    def update_symbol(filename_to_update, filename_to_save, row):
        """Update the RDS file with new data."""
        try:
            md = readRDS(filename_to_update)
            md["date"] = md["date"].dt.tz_localize("UTC")
            md["date"] = md["date"].dt.tz_convert("Asia/Kolkata")
        except Exception as e:
            get_bootlick_logger().log_warning(
                f"Failed to read RDS file {filename_to_update}: {e}",
                {"filename_to_update": filename_to_update, "error_type": type(e).__name__, "error_message": str(e)},
            )
            md = pd.DataFrame()
        md_updated = pd.concat([md, row], ignore_index=True)
        md_updated = md_updated.drop_duplicates(subset="date", keep="last")
        md_updated = md_updated.sort_values(by="date")
        md_updated.symbol = md_updated.symbol.iloc[0]
        saveRDS(md_updated, filename_to_save)

    def download_and_extract_file(url, dest_file):
        """Download and extract the ZIP file."""
        response = session.get(url)
        if response.status_code == 200:
            save_file(dest_file, response.content)
            get_bootlick_logger().log_info(f"File downloaded successfully for {p}", {"date": p})
            return read_csv_from_zip(dest_file, file_index=0, dtype=str)
        else:
            get_bootlick_logger().log_error(
                f"Failed to download file for {p}. Status code: {response.status_code}",
                None,
                {"date": p, "status_code": response.status_code},
            )
            send_mail(
                get_dynamic_config().get("from_email_id"),
                get_dynamic_config().get("to_email_id"),
                get_dynamic_config().get("from_email_password"),
                f"Unable to download future file for {p}",
                f"HTTP Status Code: {response.status_code}",
            )
        return None

    try:
        outfolder = f"{get_dynamic_config().get('daily_prices')}/fut"
        url = f"https://archives.nseindia.com/content/historical/DERIVATIVES/{valid_datetime(p,'%Y')}/{valid_datetime(p,'%b').upper()}/fo{valid_datetime(p,'%d')}{valid_datetime(p,'%b').upper()}{valid_datetime(p,'%Y')}bhav.csv.zip"
        dest_file = f"{get_dynamic_config().get('bhavcopy_folder')}/{p}_fno.zip"

        # Download and extract the data
        data = download_and_extract_file(url, dest_file)
        if data is None:
            return

        # Clean and preprocess the data
        data.columns = [col.strip() for col in data.columns]
        data = data.map(lambda x: x.strip() if isinstance(x, str) else x)
        data = data[data["OPTION_TYP"].isin(["XX", "FF"])]  # Only take future data
        if data.empty:
            get_bootlick_logger().log_info(
                "No data to import from bhavcopy. Check if future data is correct in bhavcopy.", {"data_type": "future"}
            )
            return

        # Replace 'SYMBOL' pattern
        nsenifty_pattern = r"^NIFTY$"
        data.loc[data["SYMBOL"].str.match(nsenifty_pattern), "SYMBOL"] = "NSENIFTY"

        # Convert date columns
        date_format = "%d-%b-%Y"
        data["TIMESTAMP"] = pd.to_datetime(data["TIMESTAMP"], format=date_format).dt.tz_localize("Asia/Kolkata")
        data["EXPIRY_DT"] = pd.to_datetime(data["EXPIRY_DT"], format=date_format).dt.strftime("%Y%m%d")

        # Convert numeric columns
        numeric_columns = [
            "VAL_INLAKH",
            "OPEN",
            "HIGH",
            "LOW",
            "CLOSE",
            "SETTLE_PR",
            "CONTRACTS",
            "OPEN_INT",
        ]
        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
        data["VAL_INLAKH"] = data["VAL_INLAKH"] * 100000

        # Update 'SYMBOL' column
        data.loc[:, "SYMBOL"] = data["SYMBOL"] + "_FUT_" + data["EXPIRY_DT"] + "__"

        # Process each row in the data
        for _, row in data.iterrows():
            get_bootlick_logger().log_info(f"Processing Daily Bars for {row['SYMBOL']}", {"symbol": row["SYMBOL"]})
            df = pd.DataFrame(
                {
                    "date": [row["TIMESTAMP"]],
                    "open": [row["OPEN"]],
                    "high": [row["HIGH"]],
                    "low": [row["LOW"]],
                    "close": [row["CLOSE"]],
                    "settle": [row["SETTLE_PR"]],
                    "volume": [row["CONTRACTS"]],
                    "oi": [row["OPEN_INT"]],
                    "tradevalue": [row["VAL_INLAKH"]],
                    "symbol": [row["SYMBOL"]],
                }
            )

            # Construct the filename and directory
            subdir = os.path.join(outfolder, str(row["EXPIRY_DT"]))
            filename = os.path.join(subdir, f"{row['SYMBOL']}.rds")

            # Create directory if it doesn't exist
            make_directory(subdir)
            update_symbol(filename, filename, df)

    except Exception as e:
        get_bootlick_logger().log_error(f"Error in save_future_data_old", e, {"function": "save_future_data_old"})
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Unable to process future data for {p}",
            f"{traceback.format_exc()}",
        )


def save_future_data(p: str, session, save_to_rds=True):
    """Save Future Data to Folder

    Args:
        p (str): processing date as YYYYMMDD
        session: HTTP session for making requests
    """

    def update_symbol(filename_to_update, filename_to_save, row):
        """Update the RDS file with new data."""
        try:
            md = readRDS(filename_to_update)
            md["date"] = md["date"].dt.tz_localize("UTC")
            md["date"] = md["date"].dt.tz_convert("Asia/Kolkata")
        except Exception as e:
            get_bootlick_logger().log_warning(
                f"Failed to read RDS file {filename_to_update}: {e}",
                {"filename_to_update": filename_to_update, "error_type": type(e).__name__, "error_message": str(e)},
            )
            md = pd.DataFrame()
        md_updated = pd.concat([md, row], ignore_index=True)
        md_updated = md_updated.drop_duplicates(subset="date", keep="last")
        md_updated = md_updated.sort_values(by="date")
        md_updated.symbol = md_updated.symbol.iloc[0]
        saveRDS(md_updated, filename_to_save)

    def download_and_extract_file(url, dest_file):
        """Download and extract the ZIP file."""
        response = session.get(url)
        if response.status_code == 200:
            save_file(dest_file, response.content)
            get_bootlick_logger().log_info(f"File downloaded successfully for {p}", {"date": p})
            if not save_to_rds:
                return
            return read_csv_from_zip(dest_file, file_index=0, dtype=str)
        else:
            get_bootlick_logger().log_error(
                f"Failed to download file for {p}. Status code: {response.status_code}",
                None,
                {"date": p, "status_code": response.status_code},
            )
            send_mail(
                get_dynamic_config().get("from_email_id"),
                get_dynamic_config().get("to_email_id"),
                get_dynamic_config().get("from_email_password"),
                f"Unable to download future file for {p}",
                f"HTTP Status Code: {response.status_code}",
            )
        return None

    try:
        outfolder = f"{get_dynamic_config().get('daily_prices')}/fut"
        url = f"https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{valid_datetime(p,'%Y')[0]}{valid_datetime(p,'%m')[0]}{valid_datetime(p,'%d')[0]}_F_0000.csv.zip"
        dest_file = f"{get_dynamic_config().get('bhavcopy_folder')}/{p}_fno.zip"

        # Check if destination file exists
        if file_exists_and_valid(dest_file, min_size=1000):
            get_bootlick_logger().log_info(f"File already exists: {dest_file}", {"dest_file": dest_file})
            if not save_to_rds:
                return
            data = read_csv_from_zip(dest_file, file_index=0, dtype=str)
        else:
            # Download and extract the data
            data = download_and_extract_file(url, dest_file)

        if data is None:
            return

        # Clean and preprocess the data
        data.columns = [col.strip() for col in data.columns]
        data = data.map(lambda x: x.strip() if isinstance(x, str) else x)
        data = data[data["FinInstrmTp"].isin(["STF", "IDF"])]  # Only take future data
        if data.empty:
            get_bootlick_logger().log_info(
                "No data to import from bhavcopy. Check if future data is correct in bhavcopy.", {"data_type": "future"}
            )
            return

        # Replace 'SYMBOL' pattern
        nsenifty_pattern = r"^NIFTY$"
        data.loc[data["TckrSymb"].str.match(nsenifty_pattern), "TckrSymb"] = "NSENIFTY"
        date_format = "%Y-%m-%d"

        # Convert date columns
        data["TradDt"] = pd.to_datetime(data["TradDt"], format=date_format).dt.tz_localize("Asia/Kolkata")
        data["XpryDt"] = pd.to_datetime(data["XpryDt"], format=date_format).dt.strftime("%Y%m%d")

        # Convert numeric columns
        numeric_columns = [
            "TtlTrfVal",
            "OpnPric",
            "HghPric",
            "LwPric",
            "LastPric",
            "SttlmPric",
            "TtlTradgVol",
            "OpnIntrst",
        ]
        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

        # Ensure "oi" (Open Interest) column has consistent data type
        data["OpnIntrst"] = data["OpnIntrst"].fillna(0).astype(int)

        # Update 'SYMBOL' column
        data.loc[:, "TckrSymb"] = data["TckrSymb"] + "_FUT_" + data["XpryDt"] + "__"

        # Process each row in the data
        for _, row in data.iterrows():
            get_bootlick_logger().log_info(f"Processing Daily Bars for {row['TckrSymb']}", {"symbol": row["TckrSymb"]})
            df = pd.DataFrame(
                {
                    "date": [row["TradDt"]],
                    "open": [row["OpnPric"]],
                    "high": [row["HghPric"]],
                    "low": [row["LwPric"]],
                    "close": [row["LastPric"]],
                    "settle": [row["SttlmPric"]],
                    "volume": [row["TtlTradgVol"]],
                    "oi": [row["OpnIntrst"]],  # Ensure consistent data type
                    "tradevalue": [row["TtlTrfVal"]],
                    "symbol": [row["TckrSymb"]],
                }
            )

            # Construct the filename and directory
            subdir = os.path.join(outfolder, str(row["XpryDt"]))
            filename = os.path.join(subdir, f"{row['TckrSymb']}.rds")

            # Create directory if it doesn't exist
            make_directory(subdir)
            update_symbol(filename, filename, df)

    except Exception as e:
        get_bootlick_logger().log_error(f"Error in save_future_data", e, {"function": "save_future_data"})
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Unable to process future data for {p}",
            f"{traceback.format_exc()}",
        )


def save_mf_data(p: str, session, save_to_rds=True):
    """Save Mutual Fund Data to Folder

    Args:
        p (str): Processing date as YYYYMMDD
        session: HTTP session for making requests
    """

    def update_symbol(filename_to_update, filename_to_save, row):
        """Update the RDS file with new data."""
        try:
            md = readRDS(filename_to_update)
            md["date"] = md["date"].dt.tz_localize("UTC")
            md["date"] = md["date"].dt.tz_convert("Asia/Kolkata")
        except Exception as e:
            get_bootlick_logger().log_warning(
                f"Failed to read RDS file {filename_to_update}: {e}",
                {"filename_to_update": filename_to_update, "error_type": type(e).__name__, "error_message": str(e)},
            )
            md = pd.DataFrame()
        md_updated = pd.concat([md, row], ignore_index=True)
        md_updated = md_updated.drop_duplicates(subset="date", keep="last")
        md_updated = md_updated.sort_values(by="date")
        md_updated.symbol = md_updated.symbol.iloc[-1]
        # Fill NaN values in the 'category' column with the last value of 'category'
        if "category" in md_updated.columns:
            last_category_value = md_updated["category"].iloc[-1] if not md_updated["category"].isna().all() else None
            md_updated["category"] = md_updated["category"].fillna(last_category_value)
        saveRDS(md_updated, filename_to_save)
        get_bootlick_logger().log_info(f"Updated RDS file: {filename_to_save}", {"filename_to_save": filename_to_save})

    def download_csv(url, dest_file):
        """Download the CSV file."""
        response = session.get(url)
        if response.status_code == 200:
            data = pd.read_csv(io.BytesIO(response.content), sep=";", na_values=["", " "], dtype=str)
            data = data.dropna(how="all")
            rows_to_remove = (data.isna().sum(axis=1) == len(data.columns) - 1) & data.iloc[:, 0].str.contains(
                "Mutual Fund", na=False
            )
            data = data[~rows_to_remove]
            # Transpose category to each row
            data.loc[:, "category"] = data.iloc[:, 0]  # Assuming the category is in the first column
            data["category"] = data["category"].apply(process_category)
            data["category"] = data["category"].ffill()  # Forward-fill the NaN values

            # Delete category headers
            # Keep rows where the number of NaNs is less than the total number of columns minus 2
            data = data[data.isna().sum(axis=1) < len(data.columns) - 2]
            # Rename columns
            data.columns = [
                "code",
                "scheme",
                "isin_growth_dividend",
                "isin_reinvestment",
                "nav",
                "repurchase_price",
                "sale_price",
                "date",
                "category",
            ]

            # Convert 'date' to datetime format
            data["date"] = pd.to_datetime(data["date"], format="%d-%b-%Y")

            # Change 'isin' to NaN if it does not start with 'IN'
            data["isin_growth_dividend"] = data["isin_growth_dividend"].apply(
                lambda x: x if pd.notna(x) and x.startswith("IN") else pd.NA
            )
            data["isin_reinvestment"] = data["isin_reinvestment"].apply(
                lambda x: x if pd.notna(x) and x.startswith("IN") else pd.NA
            )

            # Filter rows that have 'isin' to exclude unclaimed dividend info
            data = data[data["isin_growth_dividend"].notna() | data["isin_reinvestment"].notna()]

            # Save DataFrame to CSV
            save_pandas_in_csv_out(data, dest_file, index=True)

            get_bootlick_logger().log_info(
                f"Mutual fund file downloaded successfully for {p}", {"date": p, "file_type": "mutual_fund"}
            )
        else:
            get_bootlick_logger().log_error(
                f"Failed to download mutual fund file for {p}. Status code: {response.status_code}",
                None,
                {"date": p, "status_code": response.status_code, "file_type": "mutual_fund"},
            )
            send_mail(
                get_dynamic_config().get("from_email_id"),
                get_dynamic_config().get("to_email_id"),
                get_dynamic_config().get("from_email_password"),
                f"Unable to download mutual fund file for {p}",
                f"HTTP Status Code: {response.status_code}",
            )
            return None
        return dest_file

    # Custom function to handle the logic
    def process_category(value):
        try:
            # Check if the value can be coerced into a numeric type or is an empty string
            if value == "" or not np.isnan(pd.to_numeric(value, errors="coerce")):
                return np.nan  # Replace with NaN
        except ValueError:
            pass
        return value  # Keep the original value if it cannot be coerced

    try:
        outfolder = f"{get_dynamic_config().get('daily_prices')}/mf"
        url = f"https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={valid_datetime(p,'%d-%b-%Y')[0]}&todt={valid_datetime(p,'%d-%b-%Y')[0]}"
        dest_file = os.path.join(get_dynamic_config().get("bhavcopy_folder"), f"{p}_mf.csv")

        # Download the mutual fund data
        if dest_file is None or not file_exists_and_valid(dest_file, min_size=1000):
            dest_file = download_csv(url, dest_file)
        if not save_to_rds or dest_file is None or not file_exists_and_valid(dest_file, min_size=1000):
            return
        if file_exists_and_valid(dest_file):
            # Read CSV into a DataFrame
            data = read_csv_in_pandas_out(dest_file)
            data["category"].fillna("").astype(str)
            # Convert 'date' to timestamp and localize to 'Asia/Kolkata' timezone
            data["TIMESTAMP"] = pd.to_datetime(data["date"]).dt.tz_localize("Asia/Kolkata")

            # String manipulations and conversions
            data["SYMBOL"] = (
                data["scheme"].str.replace(" ", "", regex=False).str.replace("/", "", regex=False).str.upper()
            )
            data["Open"] = pd.to_numeric(data["nav"], errors="coerce")
            data["High"] = pd.to_numeric(data["nav"], errors="coerce")
            data["Low"] = pd.to_numeric(data["nav"], errors="coerce")
            data["Close"] = pd.to_numeric(data["nav"], errors="coerce")
            data["Volume"] = 0
            data["sale_price"] = pd.to_numeric(data["sale_price"], errors="coerce")
            data["repurchase_price"] = pd.to_numeric(data["repurchase_price"], errors="coerce")
            for i in range(len(data)):
                d = data.iloc[i]
                df = pd.DataFrame(
                    {
                        "date": [d["TIMESTAMP"]],
                        "symbol": [d["SYMBOL"]],
                        "open": [d["Open"]],
                        "high": [d["High"]],
                        "low": [d["Low"]],
                        "close": [d["Close"]],
                        "settle": [d["Close"]],
                        "volume": [d["Volume"]],
                        "sale_price": [d["sale_price"]],
                        "repurchase_price": [d["repurchase_price"]],
                        "category": [d["category"]],
                        "isin_growth_dividend": [d["isin_growth_dividend"]],
                        "isin_reinvestment": [d["isin_reinvestment"]],
                    }
                )
                get_bootlick_logger().log_info(f"Processing Daily Bars for {d['SYMBOL']}", {"symbol": d["SYMBOL"]})
                if pd.notna(d["isin_growth_dividend"]):
                    filename = os.path.join(outfolder, f"{d['isin_growth_dividend']}_MF___.rds")
                    update_symbol(filename, filename, df)

                if pd.notna(d["isin_reinvestment"]):
                    filename = os.path.join(outfolder, f"{d['isin_reinvestment']}_MF___.rds")
                    update_symbol(filename, filename, df)

            # Update the mutual fund master file
            mfmaster_data = []
            for file in list_directory(outfolder):
                if file != "mfmaster.rds":
                    file_path = os.path.join(outfolder, file)
                    md = readRDS(file_path)
                    if not md.empty:
                        last_row = md.iloc[-1]
                        mfmaster_data.append(
                            {
                                "isin": file.split("_")[0],
                                "scheme": last_row["symbol"],
                                "category": last_row["category"],
                                "lastupdate": last_row["date"],
                            }
                        )

            mfmaster = pd.DataFrame(mfmaster_data, columns=["isin", "scheme", "category", "lastupdate"])
            saveRDS(mfmaster, os.path.join(outfolder, "mfmaster.rds"))

    except Exception as e:
        get_bootlick_logger().log_error(f"Error in save_mf_data", e, {"function": "save_mf_data"})
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Unable to process mutual fund data for {p}",
            f"{traceback.format_exc()}",
        )


def save_option_data_old(p: str, session):
    """Save Option Data to Folder (Supported till and including 20240705)

    Args:
        p (str): Processing date as YYYYMMDD
        session: HTTP session for making requests
    """

    def update_symbol(filename_to_update, filename_to_save, row):
        """Update the RDS file with new data."""
        try:
            md = readRDS(filename_to_update)
            md["date"] = md["date"].dt.tz_localize("UTC")
            md["date"] = md["date"].dt.tz_convert("Asia/Kolkata")
        except Exception as e:
            get_bootlick_logger().log_warning(
                f"Failed to read RDS file {filename_to_update}: {e}",
                {"filename_to_update": filename_to_update, "error_type": type(e).__name__, "error_message": str(e)},
            )
            md = pd.DataFrame()
        md_updated = pd.concat([md, row], ignore_index=True)
        md_updated = md_updated.drop_duplicates(subset="date", keep="last")
        md_updated = md_updated.sort_values(by="date")
        md_updated.symbol = md_updated.symbol.iloc[0]
        saveRDS(md_updated, filename_to_save)

    def download_and_extract_file(url, dest_file):
        """Download and extract the ZIP file."""
        response = session.get(url)
        if response.status_code == 200:
            save_file(dest_file, response.content)
            get_bootlick_logger().log_info(f"File downloaded successfully for {p}", {"date": p})
            return read_csv_from_zip(dest_file, file_index=0, dtype=str)
        else:
            get_bootlick_logger().log_error(
                f"Failed to download file for {p}. Status code: {response.status_code}",
                None,
                {"date": p, "status_code": response.status_code},
            )
            send_mail(
                get_dynamic_config().get("from_email_id"),
                get_dynamic_config().get("to_email_id"),
                get_dynamic_config().get("from_email_password"),
                f"Unable to download option file for {p}",
                f"HTTP Status Code: {response.status_code}",
            )
        return None

    try:
        outfolder = f"{get_dynamic_config().get('daily_prices')}/opt"
        url = f"https://archives.nseindia.com/content/historical/DERIVATIVES/{valid_datetime(p,'%Y')[0]}/{valid_datetime(p,'%b')[0].upper()}/fo{valid_datetime(p,'%d')[0]}{valid_datetime(p,'%b')[0].upper()}{valid_datetime(p,'%Y')[0]}bhav.csv.zip"
        dest_file = f"{get_dynamic_config().get('bhavcopy_folder')}/{p}_fno.zip"
        data = download_and_extract_file(url, dest_file)
        if data is None:
            return

        # Clean and preprocess the data
        data.columns = [col.strip() for col in data.columns]
        data = data.map(lambda x: x.strip() if isinstance(x, str) else x)
        data = data[data["OPTION_TYP"] != "XX"]  # Exclude invalid option types
        if data.empty:
            get_bootlick_logger().log_info(
                "No data to import from bhavcopy. Check if option type is correct in bhavcopy.", {"data_type": "option"}
            )
            return

        # Replace 'SYMBOL' pattern
        nsenifty_pattern = r"^NIFTY$"
        data.loc[data["SYMBOL"].str.match(nsenifty_pattern), "SYMBOL"] = "NSENIFTY"

        # Convert date columns
        date_format = "%d-%b-%Y"
        data["TIMESTAMP"] = pd.to_datetime(data["TIMESTAMP"], format=date_format).dt.tz_localize("Asia/Kolkata")
        data["EXPIRY_DT"] = pd.to_datetime(data["EXPIRY_DT"], format=date_format).dt.strftime("%Y%m%d")

        # Convert numeric columns
        numeric_columns = [
            "VAL_INLAKH",
            "OPEN",
            "HIGH",
            "LOW",
            "CLOSE",
            "SETTLE_PR",
            "CONTRACTS",
            "OPEN_INT",
        ]
        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
        data["VAL_INLAKH"] = data["VAL_INLAKH"] * 100000

        # Update 'SYMBOL' column
        data.loc[data["OPTION_TYP"] == "XX", "SYMBOL"] = data["SYMBOL"] + "_FUT_" + data["EXPIRY_DT"] + "__"
        data.loc[data["OPTION_TYP"].isin(["PA", "PE"]), "SYMBOL"] = (
            data["SYMBOL"] + "_OPT_" + data["EXPIRY_DT"] + "_PUT_" + data["STRIKE_PR"]
        )
        data.loc[data["OPTION_TYP"].isin(["CA", "CE"]), "SYMBOL"] = (
            data["SYMBOL"] + "_OPT_" + data["EXPIRY_DT"] + "_CALL_" + data["STRIKE_PR"]
        )

        # Process each row in the data
        for _, row in data.iterrows():
            get_bootlick_logger().log_info(f"Processing Daily Bars for {row['SYMBOL']}", {"symbol": row["SYMBOL"]})
            df = pd.DataFrame(
                {
                    "date": [row["TIMESTAMP"]],
                    "open": [row["OPEN"]],
                    "high": [row["HIGH"]],
                    "low": [row["LOW"]],
                    "close": [row["CLOSE"]],
                    "settle": [row["SETTLE_PR"]],
                    "volume": [row["CONTRACTS"]],
                    "oi": [row["OPEN_INT"]],
                    "tradevalue": [row["VAL_INLAKH"]],
                    "symbol": [row["SYMBOL"]],
                }
            )

            # Construct the filename and directory
            subdir = os.path.join(outfolder, str(row["EXPIRY_DT"]))
            filename = os.path.join(subdir, f"{row['SYMBOL']}.rds")

            # Create directory if it doesn't exist
            make_directory(subdir)
            update_symbol(filename, filename, df)

    except Exception as e:
        get_bootlick_logger().log_error(f"Error in save_option_data_old", e, {"function": "save_option_data_old"})
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Unable to process option data for {p}",
            f"{traceback.format_exc()}",
        )


def save_option_data(p: str, session, save_to_rds=True):
    """Save Option Data to Folder

    Args:
        p (str): Processing date as YYYYMMDD
        session: HTTP session for making requests
    """

    def remove_trailing_zeros(value):
        if "." in value:
            return value.rstrip("0").rstrip(".") if value.rstrip("0").rstrip(".") != "" else "0"
        return value

    def update_symbol(filename_to_update, filename_to_save, row):
        """Update the RDS file with new data."""
        try:
            md = readRDS(filename_to_update)
            md["date"] = md["date"].dt.tz_localize("UTC")
            md["date"] = md["date"].dt.tz_convert("Asia/Kolkata")
        except Exception as e:
            get_bootlick_logger().log_warning(
                f"Failed to read RDS file {filename_to_update}: {e}",
                {"filename_to_update": filename_to_update, "error_type": type(e).__name__, "error_message": str(e)},
            )
            md = pd.DataFrame()
        md_updated = pd.concat([md, row], ignore_index=True)
        md_updated = md_updated.drop_duplicates(subset="date", keep="last")
        md_updated = md_updated.sort_values(by="date")
        md_updated.symbol = md_updated.symbol.iloc[0]
        saveRDS(md_updated, filename_to_save)

    def download_and_extract_file(url, dest_file):
        """Download and extract the ZIP file."""
        response = session.get(url)
        if response.status_code == 200:
            save_file(dest_file, response.content)
            get_bootlick_logger().log_info(f"File downloaded successfully for {p}", {"date": p})
            return read_csv_from_zip(dest_file, file_index=0, dtype=str)
        else:
            get_bootlick_logger().log_error(
                f"Failed to download file for {p}. Status code: {response.status_code}",
                None,
                {"date": p, "status_code": response.status_code},
            )
            send_mail(
                get_dynamic_config().get("from_email_id"),
                get_dynamic_config().get("to_email_id"),
                get_dynamic_config().get("from_email_password"),
                f"Unable to download option file for {p}",
                f"HTTP Status Code: {response.status_code}",
            )
        return None

    def get_underlying(opt_symbol):
        stk_underlying = opt_symbol.split("_")[0] + "_STK___"
        dest_file = f"/home/psharma/onedrive/rfiles/data/daily/stk/{stk_underlying}"
        if os.path.exists(dest_file):
            return stk_underlying
        stk_underlying = opt_symbol.split("_")[0] + "_IND___"
        dest_file = f"/home/psharma/onedrive/rfiles/data/daily/ind/{stk_underlying}"
        if os.path.exists(dest_file):
            return stk_underlying
        else:
            return None

    def get_settle_price(opt_symbol, expiry):
        underlying = get_underlying(opt_symbol)
        if underlying is not None:
            file_path = (
                f"{get_dynamic_config().get('daily_prices')}/stk/{underlying}"
                if "_STK_" in underlying
                else f"{get_dynamic_config().get('daily_prices')}/ind/{underlying}"
            )
            md = readRDS(file_path)
            settle_price = md.loc[md.index <= valid_datetime(expiry, "%Y-%m-%d"), "settle"][-1]
            return settle_price
        else:
            return None

    try:
        outfolder = f"{get_dynamic_config().get('daily_prices')}/opt"
        url = f"https://archives.nseindia.com/content/historical/DERIVATIVES/{valid_datetime(p,'%Y')[0]}/{valid_datetime(p,'%b')[0].upper()}/fo{valid_datetime(p,'%d')[0]}{valid_datetime(p,'%b')[0].upper()}{valid_datetime(p,'%Y')[0]}bhav.csv.zip"
        dest_file = f"{get_dynamic_config().get('bhavcopy_folder')}/{p}_fno.zip"

        # Check if destination file exists
        if file_exists_and_valid(dest_file, min_size=1000):
            get_bootlick_logger().log_info(f"File already exists: {dest_file}", {"dest_file": dest_file})
            if not save_to_rds:
                return
            data = read_csv_from_zip(dest_file, file_index=0, dtype=str)
        else:
            # Download and extract the data
            data = download_and_extract_file(url, dest_file)

        if data is None:
            return

        # Clean and preprocess the data
        data.columns = [col.strip() for col in data.columns]
        data = data.map(lambda x: x.strip() if isinstance(x, str) else x)
        data = data[data["FinInstrmTp"].isin(["STO", "IDO"])]  # only take option data
        if data.empty:
            print("No data to import from bhavcopy. Check if option type is correct in bhavcopy")
            return
        # Replacing 'SYMBOL' pattern
        nsenifty_pattern = r"^NIFTY$"
        data.loc[data["TckrSymb"].str.match(nsenifty_pattern), "TckrSymb"] = "NSENIFTY"
        date_format = "%Y-%m-%d"

        data["TradDt"] = pd.to_datetime(data["TradDt"], format=date_format).dt.tz_localize("Asia/Kolkata")
        data["XpryDt"] = pd.to_datetime(data["XpryDt"], format=date_format).dt.strftime("%Y%m%d")

        # Converting columns to numeric
        numeric_columns = [
            "TtlTrfVal",
            "OpnPric",
            "HghPric",
            "LwPric",
            "LastPric",
            "SttlmPric",
            "TtlTradgVol",
            "OpnIntrst",
        ]
        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

        # More conditional operations on 'SYMBOL'
        data["OptnTp"] = data["OptnTp"].replace({"CE": "CALL", "PE": "PUT"})
        data.loc[:, "TckrSymb"] = (
            data["TckrSymb"]
            + "_OPT_"
            + data["XpryDt"]
            + "_"
            + data["OptnTp"]
            + "_"
            + data["StrkPric"].apply(remove_trailing_zeros)
        )
        for j in range(len(data)):
            d = data.iloc[j]
            get_bootlick_logger().log_info(f"Processing Daily Bars for {d['TckrSymb']}", {"symbol": d["TckrSymb"]})
            if d["XpryDt"] == p:
                # Load underlying symbol - replace with your own logic
                underlying_settle = get_settle_price(d["TckrSymb"], d["XpryDt"])
                if underlying_settle is not None:
                    # get strike for option
                    strike = pd.to_numeric(d["StrkPric"], errors="coerce")
                    # if call
                    if d["TckrSymb"].split("_")[3] == "CALL":
                        # replace asettle for the expiration date with max(underlying$asettle,strike)-strike
                        d["SttlmPric"] = max(underlying_settle, strike) - strike
                    else:
                        # replace asettle for the expiration date with strike-min(underlying$asettle,strike)
                        d["SttlmPric"] = strike - min(underlying_settle, strike)

            df = pd.DataFrame(
                {
                    "date": [d["TradDt"]],
                    "open": [d["OpnPric"]],
                    "high": [d["HghPric"]],
                    "low": [d["LwPric"]],
                    "close": [d["LastPric"]],
                    "settle": [d["SttlmPric"]],
                    "volume": [d["TtlTradgVol"]],
                    "oi": [d["OpnIntrst"]],
                    "tradevalue": [d["TtlTrfVal"]],
                    "symbol": [d["TckrSymb"]],
                }
            )

            # Construct the filename and directory
            subdir = os.path.join(outfolder, str(d["XpryDt"]))
            filename = os.path.join(subdir, f"{d['TckrSymb']}.rds")

            # Create directory if it doesn't exist
            make_directory(subdir)
            update_symbol(filename, filename, df)

    except Exception as e:
        get_bootlick_logger().log_error(f"Error in save_option_data", e, {"function": "save_option_data"})
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Unable to process option data for {p}",
            f"{traceback.format_exc()}",
        )
