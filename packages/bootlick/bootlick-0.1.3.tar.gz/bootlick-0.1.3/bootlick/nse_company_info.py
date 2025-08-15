import datetime as dt
import io
import json
import logging
import math
import os
import re
import time
import traceback
from pathlib import Path
import pandas as pd
from chameli.dateutils import valid_datetime
from chameli.interactions import (
    file_exists_and_valid,
    read_csv_in_pandas_out,
    readRDS,
    save_file,
    save_pandas_in_csv_out,
    saveRDS,
    send_mail,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .config import get_config

# Import bootlick_logger lazily to avoid circular import
def get_bootlick_logger():
    """Get bootlick_logger instance to avoid circular imports."""
    from . import bootlick_logger
    return bootlick_logger


def get_dynamic_config():
    return get_config()


DIR = Path(__file__).parent

try:
    from nse import NSE

    nse = NSE(download_folder=DIR, server=False)
except Exception as e:
    get_bootlick_logger().log_info(f"Error initializing NSE: {e}", {
        "error_type": type(e).__name__,
        "error_message": str(e)
    })

index_constituents = readRDS(get_dynamic_config().get("index_constituents_file"))

# stock_extras = readRDS(get_dynamic_config().get("extra_stock_info_file"))


def get_nse_index_names():
    """
    Retrieves a list of NSE (National Stock Exchange) index names.
    This function fetches the list of indices from the NSE API and extracts
    their symbols (indexSymbol) into a list.
    Returns:
        list: A list of strings, where each string is the symbol of an NSE index.
    """

    out = []
    indices = nse.listIndices().get("data")
    for index in indices:
        out.append(index.get("indexSymbol"))
    return out


def get_index_info_dump(index_str):
    """
    Retrieves information about equity stocks for a given index.
    This function maps the provided index string to its corresponding NSE index name
    and database index name using a dynamic configuration. It then fetches the list
    of equity stocks associated with the NSE index.
    Args:
        index_str (str): The index identifier to retrieve information for.
    Returns:
        list: A list of equity stocks associated with the specified index.
    Notes:
        - The function relies on a dynamic configuration to map index names.
        - The `nse.listEquityStocksByIndex` method is used to fetch the stock data.
    """

    reversed_index_mapping = {v: k for k, v in get_dynamic_config().get("index_mapping").items()}
    nse_index_name = reversed_index_mapping.get(index_str, index_str)
    db_index_name = get_dynamic_config().get("index_mapping").get(index_str, index_str)
    out = nse.listEquityStocksByIndex(index=nse_index_name)
    return out


def get_etf_info_dump():
    """
    Fetches and returns a list of Exchange Traded Funds (ETFs) information.
    This function utilizes the `nse.listEtf()` method to retrieve data about
    ETFs available in the market. The returned data structure depends on the
    implementation of the `nse.listEtf()` method.
    Returns:
        list: A list containing information about ETFs.
    """

    out = nse.listEtf()
    return out


def update_index_constituents(index_str, new_symbols=None):
    """
    Updates the index constituents for a given index.
    This function retrieves and updates the list of symbols for a specified index.
    If no new symbols are provided, it fetches the symbols dynamically based on the
    index name. The function compares the new symbols with the latest entry in the
    `index_constituents` DataFrame and updates it if there are changes.
    Args:
        index_str (str): The name of the index as per NSE. This can differ from the
                         name stored in the `nse_constituents_file`.
        new_symbols (list, optional): A list of new symbols to update for the index.
                                       If None, the symbols are fetched dynamically.
    Returns:
        None: The function updates the global `index_constituents` DataFrame in place.
    Notes:
        - The function uses the `get_index_info_dump` function to fetch index data
          when `new_symbols` is not provided.
        - For the "SECURITIES IN F&O" index, it filters symbols differently compared
          to other indices.
        - The function logs whether a new row was added or if no changes were detected.
    """

    # index_str is the index name as per nse. this can be different from the name that is stored in nse_constituents_file
    global index_constituents
    if new_symbols is None:
        out = get_index_info_dump(index_str)
        if index_str == "SECURITIES IN F&O":
            new_symbols = [item.get("symbol") for item in out.get("data", []) if "symbol" in item]
        else:
            new_symbols = [item.get("symbol") for item in out.get("data") if item.get("priority") == 0]
    if not new_symbols:
        return
    new_symbols = {symbol.replace(" ", "") for symbol in new_symbols}
    new_symbols_sorted = sorted(new_symbols)
    new_symbols_str = ",".join(new_symbols_sorted)

    # Get today's date
    today_date = dt.datetime.today().strftime("%Y%m%d")

    # Determine the DataFrame index value
    df_index_value = get_dynamic_config().get("index_mapping").get(index_str, index_str.replace(" ", "").upper())

    # Get the latest entry for the index
    latest_entry = (
        index_constituents[index_constituents["index_name"] == df_index_value].sort_values("date").iloc[-1]
        if not index_constituents[index_constituents["index_name"] == df_index_value].empty
        else None
    )

    # Compare symbols and update DataFrame
    if latest_entry is None or latest_entry["symbols"] != new_symbols_str:
        # Insert a new row
        new_row = pd.DataFrame(
            [[today_date, df_index_value, new_symbols_str]], columns=["date", "index_name", "symbols"]
        )
        index_constituents = pd.concat([index_constituents, new_row], ignore_index=True)
        get_bootlick_logger().log_info(f"New row added for index {df_index_value} on date {today_date}", {
            "index_name": df_index_value,
            "date": today_date,
            "symbols_count": len(new_symbols_sorted),
            "function": "update_index_constituents"
        })
    else:
        get_bootlick_logger().log_info(f"No changes in symbols for index {df_index_value}", {
            "index_name": df_index_value,
            "date": today_date,
            "function": "update_index_constituents"
        })


def update_etf():
    """
    Updates the ETF (Exchange Traded Fund) information in the global DataFrame `index_constituents`.
    This function retrieves the latest ETF data, compares it with the existing data in the
    `index_constituents` DataFrame, and updates the DataFrame if there are any changes in the
    ETF symbols. If no changes are detected, it logs that no updates were made.
    Global Variables:
        index_constituents (pd.DataFrame): A DataFrame containing index information, including
                                           ETF symbols and their associated dates.
    Steps:
        1. Fetches the latest ETF information using the `get_etf_info_dump` function.
        2. Extracts and sorts the ETF symbols from the fetched data.
        3. Checks if there is an existing entry for the ETF index (`NSELISTEDETF`) in the
           `index_constituents` DataFrame.
        4. Compares the new symbols with the latest entry in the DataFrame.
        5. If there are changes or no existing entry, adds a new row to the DataFrame with the
           updated symbols and the current date.
        6. Logs the addition of a new row or indicates that no changes were made.
    Logs:
        - Logs a message when a new row is added to the DataFrame.
        - Logs a message if no changes are detected in the ETF symbols.
    Note:
        This function assumes that the `index_constituents` DataFrame has the following columns:
        - "date": The date of the entry in the format "YYYYMMDD".
        - "index_name": The name of the index (e.g., "NSELISTEDETF").
        - "symbols": A comma-separated string of ETF symbols.
    Raises:
        None
    Returns:
        None
    """

    global index_constituents
    out = get_etf_info_dump()
    new_symbols = [item.get("symbol") for item in out.get("data", []) if "symbol" in item]
    new_symbols_sorted = sorted(new_symbols)
    new_symbols_str = ",".join(new_symbols_sorted)
    # Determine the DataFrame index value
    df_index_value = "NSELISTEDETF"

    # Get the latest entry for the index
    latest_entry = (
        index_constituents[index_constituents["index_name"] == df_index_value].sort_values("date").iloc[-1]
        if not index_constituents[index_constituents["index_name"] == df_index_value].empty
        else None
    )
    today_date = dt.datetime.today().strftime("%Y%m%d")
    # Compare symbols and update DataFrame
    if latest_entry is None or latest_entry["symbols"] != new_symbols_str:
        # Insert a new row
        new_row = pd.DataFrame(
            [[today_date, df_index_value, new_symbols_str]], columns=["date", "index_name", "symbols"]
        )
        index_constituents = pd.concat([index_constituents, new_row], ignore_index=True)
        get_bootlick_logger().log_info(f"New row added for index {df_index_value} on date {today_date}", {
            "index_name": df_index_value,
            "date": today_date,
            "symbols_count": len(new_symbols_sorted),
            "function": "update_etf"
        })
    else:
        get_bootlick_logger().log_info(f"No changes in symbols for index {df_index_value}", {
            "index_name": df_index_value,
            "date": today_date,
            "function": "update_etf"
        })


def get_additional_stock_info(symbols):
    data_list = []
    for i, symbol in enumerate(symbols):
        try:
            get_bootlick_logger().log_info(f"Retrieving additional stock information for {symbol}: {i + 1}/{len(symbols)}", {
                "symbol": symbol,
                "progress": f"{i + 1}/{len(symbols)}",
                "total_symbols": len(symbols)
            })
            # Fetch stock quote and trade info
            quote = nse.quote(symbol)
            trade_info = nse.quote(symbol, section="trade_info")
            # Extract required fields
            update_date = quote["metadata"]["lastUpdateTime"]
            update_date = valid_datetime(update_date, "%Y%m%d")[0]
            outstanding_shares = quote["securityInfo"]["issuedSize"]
            price = quote["priceInfo"]["lastPrice"]
            circuit_band = quote["priceInfo"]["pPriceBand"]
            basic_industry = quote["industryInfo"]["basicIndustry"]
            industry = quote["industryInfo"]["industry"]
            sector = quote["industryInfo"]["sector"]
            free_float_shares = (
                int(trade_info["marketDeptOrderBook"]["tradeInfo"]["ffmc"] * 10000000 / price) if price > 0 else 0
            )

            # Append to data list
            data_list.append(
                {
                    "symbol": symbol,
                    "update_date": update_date,
                    "outstanding_shares": outstanding_shares,
                    "free_float_shares": free_float_shares,
                    "price": price,
                    "circuit_band": circuit_band,
                    "basic_industry": basic_industry,
                    "industry": industry,
                    "sector": sector,
                }
            )
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            continue
    df = pd.DataFrame(data_list)
    df["outstanding_shares"] = pd.to_numeric(df["outstanding_shares"], errors="coerce", downcast="float")
    df["free_float_shares"] = pd.to_numeric(df["free_float_shares"], errors="coerce").astype("float")
    df["update_date"] = df["update_date"].apply(lambda x: x if isinstance(x, str) else "")
    return df


def save_symbol_data(session, saveToFolder: bool = True):
    try:
        url = "https://images.5paisa.com/website/scripmaster-csv-format.csv"
        url = "https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/All"
        dest_file = f"{get_dynamic_config().get('bhavcopy_folder')}/{dt.datetime.today().strftime('%Y%m%d')}_codes.csv"
        response = session.get(url, allow_redirects=True)
        if response.status_code == 200:
            df = pd.read_csv(io.BytesIO(response.content))
            # Rename the column
            df.rename(columns={"ScripCode": "Scripcode"}, inplace=True)
            # Save the DataFrame back to CSV
            save_pandas_in_csv_out(dest_file, index=False)
            codes = read_csv_in_pandas_out(dest_file, dtype=str)
            numeric_columns = [
                "Scripcode",
                "StrikeRate",
                "LotSize",
                "QtyLimit",
                "Multiplier",
                "TickSize",
            ]
            for col in numeric_columns:
                codes[col] = pd.to_numeric(codes[col], errors="coerce")
            codes.columns = [col.strip() for col in codes.columns]
            codes = codes.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            codes = codes[
                (codes.Exch.isin(["N", "M"]))
                & (codes.ExchType.isin(["C", "D"]))
                & (codes.Series.isin(["EQ", "BE", "XX", "BZ", "RR", "IV", ""]))
            ]
            pattern = r"\d+GS\d+"
            codes = codes[~codes["Name"].str.contains(pattern, regex=True, na=True)]
            codes["long_symbol"] = None
            # Converting specific columns to numeric
            numeric_columns = ["LotSize", "TickSize", "Scripcode"]

            for col in numeric_columns:
                codes[col] = pd.to_numeric(codes[col], errors="coerce")

            # Vectorized string splitting
            codes["symbol_vec"] = codes["Name"].str.split(" ")

            # Function to process each row
            def process_row(row):
                symbol_vec = row["symbol_vec"]
                ticksize = row["TickSize"]

                if len(symbol_vec) == 1 or ticksize == 0:
                    return f"{symbol_vec[0]}_STK___" if ticksize > 0 else f"{''.join(symbol_vec)}_IND___".upper()
                elif len(symbol_vec) == 4:
                    expiry_str = f"{symbol_vec[3]}{symbol_vec[2]}{symbol_vec[1]}"
                    try:
                        expiry = dt.datetime.strptime(expiry_str, "%Y%b%d").strftime("%Y%m%d")
                        return f"{symbol_vec[0]}_FUT_{expiry}__".upper()
                    except ValueError:
                        return pd.NA
                elif len(symbol_vec) == 6:
                    expiry_str = f"{symbol_vec[3]}{symbol_vec[2]}{symbol_vec[1]}"
                    try:
                        expiry = dt.datetime.strptime(expiry_str, "%Y%b%d").strftime("%Y%m%d")
                        right = "CALL" if symbol_vec[4] == "CE" else "PUT"
                        strike = ("%f" % float(symbol_vec[5])).rstrip("0").rstrip(".")
                        return f"{symbol_vec[0]}_OPT_{expiry}_{right}_{strike}".upper()
                    except ValueError:
                        return pd.NA
                else:
                    return pd.NA

            # Apply the function to each row
            codes["long_symbol"] = codes.apply(process_row, axis=1)

            # Save to CSV
            if saveToFolder:
                dest_symbol_file = f"{get_dynamic_config().get('static_downloads')}/symbols/{dt.datetime.today().strftime('%Y%m%d')}_symbols.csv"
                save_pandas_in_csv_out(
                    codes[["long_symbol", "LotSize", "Scripcode", "Exch", "ExchType", "TickSize"]],
                    dest_symbol_file,
                    index=False,
                )
            return codes
        else:
            send_mail(
                get_dynamic_config().get("from_email_id"),
                get_dynamic_config().get("to_email_id"),
                get_dynamic_config().get("from_email_password"),
                "Unable to download symbol file from 5paisa",
                f"{traceback.format_exc()}",
            )
    except Exception:
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Unable to download symbol file for {dt.datetime.today().strftime('%Y%m%d')}",
            f"{traceback.format_exc()}",
        )


def fetch_json_with_selenium(driver, url):
    try:
        data = []
        driver.get(url)
    except Exception:
        time.sleep(3)
        driver.back()
        time.sleep(2)
        driver.forward()
        time.sleep(3)
        raw_data_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "rawdata-tab")))
        raw_data_tab.click()
        time.sleep(2)  # Wait for the raw data to load

        # Locate the element containing the raw JSON data
        raw_data_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".panelContent"))
        )
        raw_data_text = raw_data_element.text

        # Parse the JSON data
        data = json.loads(raw_data_text)
    finally:
        return data


def fetch_json_with_nseapi(category):
    out = []
    # Ensure the `nse` instance is used to call the method
    if category == "corporate-actions":
        out = nse.actions(segment="equities")
    elif category == "board-meetings":
        out = nse.boardMeetings(index="equities")  # Use the `nse` instance
    else:
        pass
    return out


def update_board_meetings(driver, update_historical_bm: bool = False):
    """
    Update board meetings using Selenium WebDriver.
    """

    def get_board_meeting(driver, symbol=None):

        if symbol is not None:
            modified_endpoint = nse_api_endpoint + "&symbol=" + symbol
        else:
            modified_endpoint = nse_api_endpoint

        try:
            # data = fetch_json_with_selenium(driver, modified_endpoint)
            data = fetch_json_with_nseapi("board-meetings")
            json_str = json.dumps(data, indent=2)
            get_bootlick_logger().log_info(f"Board Meetings :\n{json_str}", {
                "data_count": len(data) if isinstance(data, list) else 0,
                "function": "get_board_meeting"
            })
            # Process the data
            out = []
            for d in data:
                if isinstance(d, dict):
                    purpose = d.get("bm_purpose", "") + d.get("bm_desc", "")
                    if purpose != "":
                        results = ["results", "financial", "statement"]
                        dividends = ["dividend"]
                        fundraise = ["fundrai", "capitalrai"]
                        purpose_result = []
                        if any(ele in purpose.replace(" ", "").lower() for ele in results):
                            purpose_result.append("Results")
                        if any(ele in purpose.replace(" ", "").lower() for ele in dividends):
                            purpose_result.append("Dividend")
                        if any(ele in purpose.replace(" ", "").lower() for ele in fundraise):
                            purpose_result.append("FundRaise")
                        else:
                            pass
                    purpose = "/".join(purpose_result) if purpose_result else "Other"
                    date = d.get("bm_date")
                    if date is not None:
                        date = valid_datetime(date, "%Y%m%d")[0]
                    symbol = d.get("bm_symbol")
                    announce_date = d.get("bm_timestamp")
                    if announce_date is not None:
                        announce_date = valid_datetime(announce_date, "%Y%m%d-%H%M%S")[0]
                    out.append({"date": date, "symbol": symbol, "purpose": purpose, "announce_date": announce_date})
            return pd.DataFrame(out)

        except Exception as e:
            get_bootlick_logger().log_error(f"Error while fetching board meetings", e, {
                "function": "get_board_meeting"
            })
            return pd.DataFrame()

    try:
        nse_api_endpoint = get_dynamic_config().get("nse_bm_api_endpoint")
        bm = readRDS(get_dynamic_config().get("bm_file"))
        if update_historical_bm:
            symbols = symbols = list(set(bm.symbol))
            for symbol in symbols:
                bm_new = get_board_meeting(driver, symbol)
                if len(bm_new) > 0:
                    bm = pd.concat([bm, bm_new])
        else:
            bm_new = get_board_meeting(driver, symbol=None)
            if len(bm_new) > 0:
                bm = pd.concat([bm, bm_new])
        bm.reset_index(inplace=True, drop=True)

        # Normalize the 'announce_date' column to ensure consistent data types
        bm["announce_date"] = bm["announce_date"].astype(str).replace("nan", "")
        bm["announce_date_flag"] = bm["announce_date"].notna()
        bm = (
            bm.sort_values(by=["announce_date_flag", "announce_date"], ascending=[False, True])
            .drop_duplicates(["symbol", "date"])
            .drop("announce_date_flag", axis=1)
        )
        bm.sort_values("date", inplace=True)
        bm.reset_index(inplace=True, drop=True)
        saveRDS(bm, get_dynamic_config().get("bm_file"))
    except Exception:
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Error while trying to get board meetings on {dt.datetime.today().strftime('%Y%m%d')}",
            f"{traceback.format_exc()}",
        )


def update_dividends(driver, query_symbol=None):

    try:
        nse_api_endpoint = get_dynamic_config().get("nse_ca_api_endpoint")
        if query_symbol is not None:
            modified_nse_api_endpoint = nse_api_endpoint + "&symbol=" + query_symbol
        else:
            modified_nse_api_endpoint = nse_api_endpoint
        # data = fetch_json_with_selenium(driver, modified_nse_api_endpoint)
        data = fetch_json_with_nseapi("corporate-actions")
        json_str = json.dumps(data, indent=2)
        get_bootlick_logger().log_info(f"Dividends :\n{json_str}", {
            "data_count": len(data) if isinstance(data, list) else 0,
            "function": "update_dividends"
        })
        out = []
        for d in data:
            if isinstance(d, dict):
                symbol = d.get("symbol")
                fv = d.get("faceVal")
                if fv is not None:
                    fv = float(fv)
                ex_date = d.get("exDate")
                if ex_date is not None:
                    ex_date = valid_datetime(ex_date, "%Y%m%d")[0]
                subject = d.get("subject").lower()
                if subject is not None:
                    dividend_list = subject.split("dividend")[1:]
                    if len(dividend_list) > 0:
                        d_formatted = json.dumps(d, indent=4)
                        get_bootlick_logger().log_info(f"Dividend :\n{d_formatted}", {
                            "symbol": symbol,
                            "ex_date": ex_date,
                            "function": "update_dividends"
                        })
                        for d in dividend_list:
                            if re.search("bonus", d) is None and re.search("split", d) is None:
                                temp = re.findall(r"([0-9][,.]*[0-9]*)|$", d)[0]
                                if temp != "":
                                    out.append({"date": ex_date, "symbol": symbol, "dps": float(temp), "fv": fv})
                                else:
                                    out.append({"date": ex_date, "symbol": symbol, "dps": 0, "fv": fv})
        out = pd.DataFrame(out)
        div = readRDS(get_dynamic_config().get("div_file"))
        if len(out) > 0:
            div = pd.concat([div, out])
            div = div.sort_values(by=["date", "dps"], ascending=[True, False]).drop_duplicates(["symbol", "date", "fv"])
            div.reset_index(inplace=True, drop=True)
            div.sort_values("date", inplace=True)
        saveRDS(div, get_dynamic_config().get("div_file"))
    except Exception:
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Error while trying to get dividends on {dt.datetime.today().strftime('%Y%m%d')}",
            f"{traceback.format_exc()}",
        )


def update_split_bonus(driver, query_symbol=None):

    out = []
    nse_api_endpoint = get_dynamic_config().get("nse_ca_api_endpoint")
    try:
        if query_symbol is not None:
            modified_nse_api_endpoint = nse_api_endpoint + "&symbol=" + query_symbol
        else:
            modified_nse_api_endpoint = nse_api_endpoint
        # data = fetch_json_with_selenium(driver, modified_nse_api_endpoint)
        data = fetch_json_with_nseapi("corporate-actions")
        json_str = json.dumps(data, indent=4)
        get_bootlick_logger().log_info(f"Splits and Bonus :\n{json_str}", {
            "data_count": len(data) if isinstance(data, list) else 0,
            "function": "update_split_bonus"
        })
        for d in data:
            if isinstance(d, dict):
                symbol = d.get("symbol")
                ex_date = d.get("exDate")
                if ex_date is not None:
                    ex_date = valid_datetime(ex_date, "%Y%m%d")[0]
                subject = d.get("subject").lower()
                if subject is not None:
                    bonus_list = subject.split("bonus")[1:]
                    if len(bonus_list) > 0:
                        d_formatted = json.dumps(d, indent=4)
                        get_bootlick_logger().log_info(f"Bonus :\n{d_formatted}", {
                            "symbol": symbol,
                            "ex_date": ex_date,
                            "function": "update_split_bonus"
                        })
                        d = bonus_list[0]
                        numbers = re.findall(r"\d+|$", d)
                        if len(numbers) >= 2:
                            new_shares = int(re.findall(r"\d+|$", d)[0])
                            old_shares = int(re.findall(r"\d+|$", d)[1])
                            new_shares = new_shares + old_shares
                            gcd = math.gcd(old_shares, new_shares)
                            old_shares = old_shares / gcd
                            new_shares = new_shares / gcd
                            out.append(
                                {
                                    "date": ex_date,
                                    "symbol": symbol,
                                    "oldshares": old_shares,
                                    "newshares": new_shares,
                                    "purpose": "Bonus",
                                }
                            )
                    split_list = subject.split("split")[1:]
                    if len(split_list) > 0:
                        d_formatted = json.dumps(d, indent=4)
                        get_bootlick_logger().log_info(f"Bonus :\n{d_formatted}", {
                            "symbol": symbol,
                            "ex_date": ex_date,
                            "function": "update_split_bonus"
                        })
                        d = split_list[0]
                        numbers = re.findall(r"\d+|$", d)
                        if len(numbers) >= 2:
                            new_shares = int(re.findall(r"\d+|$", d)[0])
                            old_shares = int(re.findall(r"\d+|$", d)[1])
                            gcd = math.gcd(old_shares, new_shares)
                            old_shares = old_shares / gcd
                            new_shares = new_shares / gcd
                            out.append(
                                {
                                    "date": ex_date,
                                    "symbol": symbol,
                                    "oldshares": old_shares,
                                    "newshares": new_shares,
                                    "purpose": "Split",
                                }
                            )
        out = pd.DataFrame(out)
        splits = readRDS(get_dynamic_config().get("splits_file"))
        if len(out) > 0:
            splits = pd.concat([splits, out])
            splits = splits.sort_values(by=["date"], ascending=[True]).drop_duplicates(
                ["symbol", "date", "oldshares", "newshares"]
            )
            splits.reset_index(inplace=True, drop=True)
            splits.sort_values("date", inplace=True)
        saveRDS(splits, get_dynamic_config().get("splits_file"))
    except Exception:
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Error while trying to get splits and bonuses on {dt.datetime.today().strftime('%Y%m%d')}",
            f"{traceback.format_exc()}",
        )


def get_symbol_change(session):
    try:
        symbolchange_old = readRDS(get_dynamic_config().get("symbolchange_file"))
        symbolchange_old["effectivedate"] = symbolchange_old["effectivedate"].dt.tz_localize("UTC")
        symbolchange_old["effectivedate"] = symbolchange_old["effectivedate"].dt.tz_convert("Asia/Kolkata")

        url = "https://archives.nseindia.com/content/equities/symbolchange.csv"
        dest_file = f"{get_dynamic_config().get('static_downloads')}/downloads/symbolchange_{dt.datetime.today().strftime('%Y%m%d')}.csv"
        if not os.path.exists(dest_file):
            # Downloading the file
            response = session.get(url)
            if response.status_code == 200:
                save_file(dest_file, response.content)
            else:
                send_mail(
                    get_dynamic_config().get("from_email_id"),
                    get_dynamic_config().get("to_email_id"),
                    get_dynamic_config().get("from_email_password"),
                    f"Error while trying to download symbolchange.csv {dt.datetime.today().strftime('%Y%m%d')}",
                    "Pleae re-run python script",
                )

        if file_exists_and_valid(dest_file, min_size=1):
            symbolchange_new = read_csv_in_pandas_out(dest_file, encoding="latin1", header=None, dtype=str)
            if symbolchange_new.iloc[0, 3] == "SM_APPLICABLE_FROM":
                symbolchange_new = pd.read_csv(dest_file, encoding="latin1", header=True, dtype=str)
            else:
                symbolchange_new.columns = ["SYMB_COMPANY_NAME", "SM_KEY_SYMBOL", "SM_NEW_SYMBOL", "SM_APPLICABLE_FROM"]

            if len(symbolchange_new) > 0:
                # Convert 'SM_APPLICABLE_FROM' to datetime with the specified format
                symbolchange_new["SM_APPLICABLE_FROM"] = pd.to_datetime(
                    symbolchange_new["SM_APPLICABLE_FROM"], format="%d-%b-%Y"
                )
                symbolchange_new["SM_APPLICABLE_FROM"] = symbolchange_new["SM_APPLICABLE_FROM"].dt.tz_localize(
                    "Asia/Kolkata"
                )
                # Create a new DataFrame 'md1' with selected columns
                md1 = symbolchange_new[["SM_APPLICABLE_FROM", "SM_KEY_SYMBOL", "SM_NEW_SYMBOL"]].copy()
                md1.columns = ["effectivedate", "oldsymbol", "newsymbol"]
                md1 = md1.loc[md1.oldsymbol != md1.newsymbol,]
                symbolchange = pd.concat([symbolchange_old, md1], ignore_index=True)
                symbolchange = symbolchange.drop_duplicates()
                symbolchange = symbolchange[
                    symbolchange.oldsymbol != "LIST000857"
                ]  # hardcoding this exclusion as csv has this erroneous row for BHARTIHEXA
                symbolchange = symbolchange.sort_values(by="effectivedate")
                # Resetting the index
                symbolchange.reset_index(drop=True, inplace=True)
                saveRDS(symbolchange, get_dynamic_config().get("symbolchange_file"))
    except Exception:
        send_mail(
            get_dynamic_config().get("from_email_id"),
            get_dynamic_config().get("to_email_id"),
            get_dynamic_config().get("from_email_password"),
            f"Unable to download symbolchange file for {dt.datetime.today().strftime('%Y%m%d')}",
            f"{traceback.format_exc()}",
        )
