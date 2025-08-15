from collections import OrderedDict
import os
import sys
from typing import List
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import logging
from bs4 import BeautifulSoup
import time
import random
import concurrent.futures
import psutil
import re
import glob
import yaml
import datetime as dt
from chameli.interactions import readRDS, saveRDS, get_session_or_driver
from .config import get_config

# Import bootlick_logger lazily to avoid circular import
def get_bootlick_logger():
    """Get bootlick_logger instance to avoid circular imports."""
    from . import bootlick_logger
    return bootlick_logger


def get_dynamic_config():
    return get_config()


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.70 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

# COACode - Standard Character Code for Ledger Name
# EndDate - End Date for the period if PnL/CF Item, else date of snapshot
# FiscalYear - Fiscal Year for the EndDate
# FiscalPeriodNumber - Period Number between 1-4, but it could be 5 too if there is a change in reporting period midyear
# PeriodType - Type of period - Annual if corresponding to Annual (12 mth or equiv reporting) else Interim
# PeriodLength - No of months in period if item is from PnL/CF
# Symbol - Company Name


def handle_cash_flows_section(driver):
    try:
        # Locate the Cash Flows section
        cash_flows_section = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='responsive-holder fill-card-width'][@data-result-table]")
            )
        )
        # Find all buttons inside the section
        cash_flows_buttons = cash_flows_section.find_elements(By.XPATH, ".//tr[contains(@class, 'expandable')]//button")

        if not cash_flows_buttons:
            get_bootlick_logger().log_error("No Cash Flows buttons found.", None, {"function": "handle_cash_flows_section"})
            return

        for index, button in enumerate(cash_flows_buttons):
            retries = 0
            while retries < 3:
                try:
                    # Scroll the button into view
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)

                    # Use JavaScript click as a fallback if regular click doesn't work
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(2)  # Small delay for dynamic content

                    # Check if the section expanded
                    if is_section_expanded(button):
                        get_bootlick_logger().log_debug(f"Successfully clicked and expanded Cash Flows button {index + 1}", {"button_index": index + 1, "function": "handle_cash_flows_section"})
                        break
                    else:
                        get_bootlick_logger().log_debug(f"Cash Flows button {index + 1} did not expand. Retrying...", {"button_index": index + 1, "function": "handle_cash_flows_section"})
                        retries += 1

                except (StaleElementReferenceException, TimeoutException) as e:
                    get_bootlick_logger().log_debug(f"Retry {retries + 1}: Failed to click Cash Flows button {index + 1} due to {e}", {"retry_count": retries + 1, "button_index": index + 1, "error_type": type(e).__name__, "function": "handle_cash_flows_section"})
                    retries += 1
                except Exception as e:
                    get_bootlick_logger().log_debug(f"Failed to click Cash Flows button {index + 1}: {e}", {"button_index": index + 1, "error_type": type(e).__name__, "function": "handle_cash_flows_section"})
                    retries += 1

    except Exception as e:
        get_bootlick_logger().log_debug(f"Error handling Cash Flows section: {e}", {"error_type": type(e).__name__, "function": "handle_cash_flows_section"})


def is_section_expanded(button):
    try:
        # Check if the row below the button is now visible
        parent_row = button.find_element(By.XPATH, "../..")
        expanded_row = parent_row.find_element(By.XPATH, "following-sibling::tr[contains(@class, 'child-row')]")
        return expanded_row.is_displayed()
    except Exception:
        return False


def wait_for_complete_load(driver, timeout=30):
    """Wait until the page is fully loaded, network is idle, and status bar is clear."""
    get_bootlick_logger().log_debug("Waiting for page load to complete...", {"function": "wait_for_complete_load"})

    # Wait for document readyState to be 'complete'
    WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
    get_bootlick_logger().log_debug("Document is fully loaded.", {"function": "wait_for_complete_load"})

    # # Wait for network to be idle
    # WebDriverWait(driver, timeout).until(
    #     lambda d: d.execute_script("return performance.getEntries().filter(e => e.duration === 0).length === 0")
    # )
    # logger.info("Network is idle.")

    # Wait for the status bar message to clear
    WebDriverWait(driver, timeout).until(
        lambda d: "transferring data" not in d.execute_script("return window.status || '';")
    )
    get_bootlick_logger().log_debug("Status bar is clear.", {"function": "wait_for_complete_load"})


# Robust `parse_symbol` function with proxy handling and retries
def parse_symbol(symbol, driver, consolidated):
    complete = True
    cash_flows_buttons_to_wait_for = [
        "//button[contains(@onclick, \"Company.showSchedule('Cash from Operating Activity', 'cash-flow', this)\")]",
        "//button[contains(@onclick, \"Company.showSchedule('Cash from Investing Activity', 'cash-flow', this)\")]",
        "//button[contains(@onclick, \"Company.showSchedule('Cash from Financing Activity', 'cash-flow', this)\")]",
    ]
    if consolidated:
        url = f"https://www.screener.in/company/{symbol}/consolidated/"
    else:
        url = f"https://www.screener.in/company/{symbol}/"
    try:
        # Open the URL
        driver.get(url)
        wait_for_complete_load(driver)
        scroll_to_bottom_multiple_times(driver)
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@onclick, 'Company.showSchedule')]"))
        )
        for button_xpath in cash_flows_buttons_to_wait_for:
            try:
                button = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, button_xpath)))
            except Exception as button_error:
                get_bootlick_logger().log_debug(f"Failed to load button for {symbol}: {button_xpath}", {"symbol": symbol, "button_xpath": button_xpath, "function": "parse_symbol"})

        # Click on all expandable rows using button elements with specific onclick attributes
        expandable_buttons = driver.find_elements(By.XPATH, "//button[contains(@onclick, 'Company.showSchedule')]")
        for button in expandable_buttons:
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button)).click()
            except Exception as e:
                get_bootlick_logger().log_debug(f"Failed to click button: {e}", {"error_type": type(e).__name__, "function": "parse_symbol"})

        wait_for_complete_load(driver)
        scroll_to_bottom_multiple_times(driver)
        expandable_buttons = driver.find_elements(By.XPATH, "//button[contains(@onclick, 'Company.showSchedule')]")
        for button in expandable_buttons:
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button)).click()
            except Exception as e:
                get_bootlick_logger().log_debug(f"Failed to click button: {e}", {"error_type": type(e).__name__, "function": "parse_symbol"})

        # Click on Shareholding Pattern expandable buttons specifically
        try:
            shareholding_section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "quarterly-shp"))
            )
            shareholding_buttons = shareholding_section.find_elements(
                By.XPATH, ".//button[contains(@onclick, 'Company.showShareholders')]"
            )
            for button in shareholding_buttons:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button)).click()
            wait_for_complete_load(driver)
            scroll_to_bottom_multiple_times(driver)
            shareholding_buttons = shareholding_section.find_elements(
                By.XPATH, ".//button[contains(@onclick, 'Company.showShareholders')]"
            )
            for button in shareholding_buttons:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button)).click()
        except Exception as e:
            get_bootlick_logger().log_debug(f"Failed to click Shareholding Pattern button: {e}", {"error_type": type(e).__name__, "function": "parse_symbol"})

        # Get page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract company name
        company_name = soup.find("h1", class_="margin-0").text.strip()
        consolidated_found = soup.body.find_all(string=lambda text: text and "consolidated" in text.lower())
        if not consolidated and consolidated_found:
            get_bootlick_logger().log_error(f"Consolidated data found while attempting to parse unconsildated {symbol}.", None, {"symbol": symbol, "function": "parse_symbol"})
            return {}

        # Function to extract table data with child rows
        def extract_table_data(table):
            headers = [th.text.strip() for th in table.find_all("th")]
            rows_data = []
            for row in table.find_all("tr")[1:]:
                row_data = [td.text.strip() for td in row.find_all("td")]
                if row_data:
                    row_data.insert(0, company_name)
                    row_data[1] = row_data[1].replace("\xa0", " ").strip()
                    if (
                        len(row_data) > 1
                        and not any("padding-left" in td.get("style", "") for td in row.find_all("td"))
                        and not row_data[1].endswith("-")
                    ):
                        row_data[1] += " -"
                    row_data.insert(0, symbol)
                    for i in range(3, len(row_data)):
                        try:
                            row_data[i] = float(row_data[i].replace(",", "").replace("%", ""))
                        except ValueError:
                            row_data[i] = float("nan")
                    rows_data.append(row_data)
                    # Check if the row has child rows
                    child_rows = row.find_next("tr", class_="child-row")
                    while child_rows:
                        child_data = [td.text.strip() for td in child_rows.find_all("td")]
                        child_data.insert(0, company_name)
                        child_data.insert(0, symbol)
                        for i in range(3, len(child_data)):
                            try:
                                child_data[i] = float(child_data[i].replace(",", ""))
                            except ValueError:
                                child_data[i] = float("nan")
                        rows_data.append(child_data)
                        child_rows = child_rows.find_next_sibling("tr", class_="child-row")
            return pd.DataFrame(rows_data, columns=["Symbol", "Company", "Description"] + headers[1:])

        def extract_shareholding_table(table):
            headers = [th.text.strip() for th in table.find_all("th")]
            rows_data = []

            parent_category = None  # To track the current parent category

            for row in table.find_all("tr")[1:]:
                row_data = [td.text.strip() for td in row.find_all("td")]
                if row_data:
                    # Check if it's a parent row with a button (expandable)
                    button = row.find("button")
                    if button:
                        parent_category = button.text.replace("\xa0", " ").strip().rstrip("-").strip()
                        description = parent_category
                    else:
                        # For sub-rows, prepend the parent category to the description
                        description = row_data[0].strip().replace("\xa0", " ").strip().rstrip("-").strip()
                        if parent_category:
                            description = f"{parent_category}: {description}"
                    row_data.insert(0, symbol)
                    row_data.insert(1, company_name)
                    row_data[2] = description
                    for i in range(3, len(row_data)):
                        try:
                            row_data[i] = float(row_data[i].replace(",", "").replace("%", ""))
                        except ValueError:
                            row_data[i] = float("nan")
                    rows_data.append(row_data)
            # Return the parsed data as a DataFrame
            sorted_headers = sorted(headers[1:], key=lambda x: datetime.strptime(x, "%b %Y"))
            df = pd.DataFrame(rows_data, columns=["Symbol", "Company", "Description"] + sorted_headers)
            # Handle duplicate descriptions by summing values
            df = df.groupby(["Symbol", "Company", "Description"], as_index=False).sum(numeric_only=True)
            return df

        # Extract balance sheet, P&L, cash flows, shareholding pattern, and quarterly results sections
        sections = {
            "Balance Sheet": pd.DataFrame(),
            "Profit & Loss": pd.DataFrame(),
            "Quarterly Results": pd.DataFrame(),
            "Cash Flows": pd.DataFrame(),
            "Shareholding Pattern": pd.DataFrame(),
        }

        for section_name, df in sections.items():
            section = soup.find("h2", text=section_name)
            if section:
                table = section.find_next("table")
                if table:
                    if section_name != "Shareholding Pattern":
                        extracted_df = extract_table_data(table)
                    else:
                        extracted_df = extract_shareholding_table(table)
                    extracted_df["COACode"] = extracted_df["Description"].map(
                        get_dynamic_config().get(section_name, {})
                    )
                    if section_name != "Shareholding Pattern":
                        extracted_df = extracted_df[extracted_df["COACode"].str.strip() != ""]
                    extracted_df["COACode"] = extracted_df["COACode"].fillna("").astype(str)
                    if (
                        not save_eligible(section_name, extracted_df)
                        or extracted_df.Description.str.endswith("+ -").any()
                        or extracted_df.Description.str.endswith("+").any()
                    ):
                        get_bootlick_logger().log_info(f"Missing data for {symbol}:{section}. Skipping", {"symbol": symbol, "section": section, "function": "parse_symbol"})
                        complete = False
                    else:
                        if complete:
                            sections[section_name] = pd.concat([df, extracted_df], ignore_index=True)
                else:
                    get_bootlick_logger().log_debug(f"Did not find data for {section} for {symbol}", {"symbol": symbol, "section": section, "function": "parse_symbol"})
        if complete:
            get_bootlick_logger().log_info(f"Completed parsing data for {symbol}", {"symbol": symbol, "function": "parse_symbol"})
            return sections
        else:
            get_bootlick_logger().log_info(f"incomplete parsing data for {symbol}. Skipping", {"symbol": symbol, "function": "parse_symbol"})
            return {}

    except Exception as e:
        get_bootlick_logger().log_error(f"Failed to parse {symbol}", e, {"symbol": symbol, "function": "parse_symbol"})
        if driver:
            driver.quit()
        raise


def scroll_to_bottom_multiple_times(driver, max_scrolls=5):
    """Scroll to the bottom of the page multiple times."""
    for i in range(max_scrolls):
        get_bootlick_logger().log_debug(f"Scrolling attempt {i + 1}...", {"scroll_attempt": i + 1, "function": "scroll_to_bottom_multiple_times"})
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Allow time for content to load

        # Check if more content has loaded
        new_height = driver.execute_script("return document.body.scrollHeight;")
        if new_height == driver.execute_script("return window.pageYOffset + window.innerHeight;"):
            get_bootlick_logger().log_debug("Reached the bottom of the page.", {"function": "scroll_to_bottom_multiple_times"})
            break


# Function to attempt parsing with timeout and proxy retry
def parse_with_timeout(symbol, driver, consolidated, timeout=60):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(parse_symbol, symbol, driver, consolidated)
        try:
            result = future.result(timeout=timeout)  # Timeout after 20 seconds
            return result  # If parsing is successful, move to next symbol
        except concurrent.futures.TimeoutError:
            get_bootlick_logger().log_debug(f"Timeout reached for {symbol}.Switching proxy...", {"symbol": symbol, "function": "parse_with_timeout"})
            driver.quit()
            kill_firefox_processes()
            raise


def kill_firefox_processes():
    for process in psutil.process_iter():
        try:
            if process.name().lower() in ["firefox", "geckodriver"]:
                process.kill()
        except psutil.NoSuchProcess:
            continue


def symbol_exists(symbol: str, data_folder: str):
    """
    Check if a file for the given symbol exists in the specified data folder.

    Args:
        symbol (str): The symbol to check.
        data_folder (str): The folder where the data files are stored.

    Returns:
        bool
    """
    filename = f"Cash Flows_{symbol}.rds"
    file_path = os.path.join(data_folder, filename)
    return os.path.exists(file_path)


# Initialize a global set to track unique resource URLs and a cumulative total
cumulative_data_consumed = 0
seen_resources = set()


def log_data_consumed(driver):
    """
    Logs the total data consumed during the current WebDriver session across all page loads.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        int: Total data consumed in bytes during the session.
    """
    global cumulative_data_consumed, seen_resources
    try:
        # Get the performance entries for the current page
        performance_data = driver.execute_script("return performance.getEntriesByType('resource');")

        # Calculate the data consumed for new resources only
        session_data_consumed = 0
        for entry in performance_data:
            resource_url = entry.get("name", "")
            transfer_size = entry.get("transferSize", 0)
            if resource_url not in seen_resources:
                seen_resources.add(resource_url)
                session_data_consumed += transfer_size

        # Add the session data to the cumulative total
        cumulative_data_consumed += session_data_consumed

        # Log the data consumed for the current session and cumulative total
        get_bootlick_logger().log_info(f"Data consumed in this session: {session_data_consumed / 1024:.2f} KB", {"session_data_consumed_kb": session_data_consumed / 1024, "function": "log_data_consumed"})
        get_bootlick_logger().log_info(f"Cumulative data consumed so far: {cumulative_data_consumed / 1024:.2f} KB", {"cumulative_data_consumed_kb": cumulative_data_consumed / 1024, "function": "log_data_consumed"})

        return session_data_consumed
    except Exception as e:
        get_bootlick_logger().log_error(f"Failed to log data consumed", e, {"function": "log_data_consumed"})
        return 0


# Main function to process symbols with retry logic and intermediate saving
def process_symbols(
    proxy_source, proxy_user, proxy_pass, api_key, driver_path, symbols, data_folder, refresh, incomplete_check
) -> List[str]:
    driver = None
    unsuccessul_symbols = []
    try:
        driver = get_session_or_driver(
            url_to_test="https://screener.in",
            get_session=False,
            headless=False,
            proxy_source=proxy_source,
            api_key=api_key,
            proxy_user=proxy_user,
            proxy_password=proxy_pass,
            webdriver_path=driver_path,
        )
        os.makedirs(data_folder, exist_ok=True)

        for symbol in symbols:
            if not refresh and symbol_exists(symbol, data_folder):
                if (not incomplete_check) or (
                    incomplete_check
                    and not (
                        readRDS(f"{data_folder}/Balance Sheet_{symbol}.rds").iloc[:, -2].isna().any()
                        or readRDS(f"{data_folder}/Cash Flows_{symbol}.rds").iloc[:, -2].isna().any()
                    )
                ):
                    get_bootlick_logger().log_debug(f"Skipping already processed symbol: {symbol}", {"symbol": symbol, "function": "process_symbols"})
                    continue
            get_bootlick_logger().log_info(f"Loading: {symbol}:{symbols.index(symbol)}/{len(symbols)}", {"symbol": symbol, "progress": f"{symbols.index(symbol)}/{len(symbols)}", "total_symbols": len(symbols), "function": "process_symbols"})
            delay = random.uniform(2, 5)
            get_bootlick_logger().log_info(f"Waiting for {delay:.2f} seconds...", {"delay_seconds": delay, "function": "process_symbols"})
            time.sleep(delay)
            retries = 2
            consolidated = True
            while retries > 0:
                try:
                    if retries == 1:
                        consolidated = False
                    sections = parse_with_timeout(symbol, driver, consolidated)
                    if sections and isinstance(sections, dict):
                        for section, df in sections.items():
                            temp_file = os.path.join(data_folder, f"{section}_{symbol}.rds")
                            log_data_consumed(driver)
                            saveRDS(df, temp_file)
                        break  # Exit loop on success
                    else:
                        get_bootlick_logger().log_warning(f"No valid sections returned for symbol {symbol}. Retrying...", {"symbol": symbol, "function": "process_symbols"})
                        log_data_consumed(driver)
                        retries -= 1
                        if retries == 0:
                            unsuccessul_symbols.append(symbol)
                except Exception as e:
                    get_bootlick_logger().log_error(f"Error processing symbol {symbol} on retry {2 - retries}", e, {"symbol": symbol, "retry_count": 2 - retries, "function": "process_symbols"})
                    get_bootlick_logger().log_warning(f"Retrying {symbol} with a new proxy...", {"symbol": symbol, "function": "process_symbols"})
                    retries -= 1
                    if driver:
                        driver.quit()
                    driver = get_session_or_driver(
                        url_to_test="https://screener.in",
                        get_session=False,
                        headless=False,
                        proxy_source=proxy_source,
                        api_key=api_key,
                        proxy_user=proxy_user,
                        proxy_password=proxy_pass,
                        webdriver_path=driver_path,
                    )
    finally:
        if driver:
            driver.quit()
        get_bootlick_logger().log_info(f"Total data consumed across all sessions: {cumulative_data_consumed / 1024:.2f} KB", {"cumulative_data_consumed_kb": cumulative_data_consumed / 1024, "function": "process_symbols"})
        return unsuccessul_symbols


def consolidate_section_data(section, temp_folder, existing_data, output_path):
    """Consolidate all temp files for a section and merge with existing data."""
    temp_files = glob.glob(os.path.join(temp_folder, f"{section}_*.rds"))

    # Load and concatenate all temp files
    df = pd.concat([readRDS(file) for file in temp_files], ignore_index=True)
    df = df.copy()

    # Normalize and deduplicate new data
    df["Normalized_Description"] = df["Description"].str.rstrip("+ -").str.strip()

    # Clean and normalize column names
    df.columns = [
        re.search(r"[A-Za-z]{3} \d{4}", col).group() if re.search(r"[A-Za-z]{3} \d{4}", col) else col
        for col in df.columns
    ]

    # Identify date columns
    date_columns = [col for col in df.columns if re.match(r"^[A-Za-z]{3} \d{4}$", col)]

    # Melt the date columns into rows to create an "EndDate" column
    df = df.melt(
        id_vars=["Symbol", "Company", "Description", "Normalized_Description"],
        value_vars=date_columns,
        var_name="EndDate",
        value_name="Value",
    )

    # Drop rows with NaN values in the "Value" column
    df = df.dropna(subset=["Value"])

    # Normalize and deduplicate existing data
    existing_data[section]["Normalized_Description"] = (
        existing_data[section]["Description"].str.rstrip("+ -").str.strip()
    )

    # Melt existing_data[section] to create an "EndDate" column
    existing_date_columns = [col for col in existing_data[section].columns if re.match(r"^[A-Za-z]{3} \d{4}$", col)]
    existing_data_long = existing_data[section].melt(
        id_vars=["Symbol", "Company", "Description", "Normalized_Description"],
        value_vars=existing_date_columns,
        var_name="EndDate",
        value_name="Value",
    )

    # Drop rows with NaN values in the "Value" column for existing data
    existing_data_long = existing_data_long.dropna(subset=["Value"])

    # Merge existing data with new data
    merged_data = pd.concat([existing_data_long, df], ignore_index=True)

    # Overwrite rows in `merged_data` with data from `df` for matching (Symbol, Normalized_Description, EndDate)
    merged_data = (
        merged_data.sort_values(by=["Symbol", "Normalized_Description", "EndDate"], ascending=[True, True, False])
        .drop_duplicates(subset=["Symbol", "Normalized_Description", "EndDate"], keep="first")
        .reset_index(drop=True)
    )
    merged_data["COACode"] = merged_data["Description"].map(get_dynamic_config().get(section, {}))
    # Pivot the data back to wide format
    merged_data = merged_data.pivot(
        index=["Symbol", "Company", "Description", "Normalized_Description", "COACode"],
        columns="EndDate",
        values="Value",
    ).reset_index()
    # Sort and reorder columns
    fixed_columns = ["Symbol", "Company", "Description", "COACode"]
    date_columns = [
        col for col in merged_data.columns if col not in fixed_columns and re.match(r"^[A-Za-z]{3} \d{4}$", col)
    ]
    sorted_date_columns = sorted(date_columns, key=lambda x: datetime.strptime(x, "%b %Y"))
    merged_data = merged_data[fixed_columns + sorted_date_columns]

    # Map COACode for the section
    merged_data["COACode"] = merged_data["Description"].map(get_dynamic_config().get(section, {}))

    # Save consolidated data
    saveRDS(merged_data, output_path)
    get_bootlick_logger().log_info(f"Section '{section}' saved with updated data.", {"section": section, "function": "consolidate_section_data"})


def save_eligible(section, df):
    non_numeric_columns = ["Symbol", "Company", "Description", "COACode"]

    # Only drop columns that exist in the DataFrame
    financial_columns = df.drop(columns=[col for col in non_numeric_columns if col in df.columns], errors="ignore")

    # Check if all values in the remaining columns are NaN
    if financial_columns.isna().all().all():
        get_bootlick_logger().log_info(f"All values for {section} are NaNs. Skipping save.", {"section": section, "function": "consolidate_section_data"})
        return False

    return True


def save_section_data(section, df):
    global existing_data

    # Skip if all values in df are NaN
    if not save_eligible(section, df):
        return

    # Filter existing_data[section] for only relevant symbols from df
    relevant_existing_rows = existing_data[section][existing_data[section]["Symbol"].isin(df["Symbol"])].copy()

    # Normalize descriptions in both DataFrames
    relevant_existing_rows["Normalized_Description"] = (
        relevant_existing_rows["Description"].str.rstrip("+ -").str.rstrip("-").str.strip()
    )
    relevant_existing_rows = relevant_existing_rows.drop_duplicates(
        subset=["Symbol", "Normalized_Description"], keep="last"
    )
    df["Normalized_Description"] = df["Description"].str.rstrip("+ -").str.rstrip("-").str.strip()

    # Set index for efficient updates
    relevant_existing_rows = relevant_existing_rows.set_index(["Symbol", "Normalized_Description"])

    # Update existing rows with new data
    relevant_existing_rows.update(df.set_index(["Symbol", "Normalized_Description"]))

    # Reset the index to restore the original structure
    relevant_existing_rows = relevant_existing_rows.reset_index()

    # Step 3: Merge df with relevant_existing_rows
    merged_data = pd.concat([relevant_existing_rows, df]).drop_duplicates(
        subset=["Symbol", "Normalized_Description"], keep="last"
    )

    # Step 1: Create combined description order using OrderedDict
    combined_order = OrderedDict()

    # Add descriptions from df to combined_order
    for desc in df["Normalized_Description"]:
        combined_order[desc] = None

    # Add descriptions from relevant_existing_rows that are not in df
    for desc in relevant_existing_rows["Normalized_Description"]:
        if desc not in combined_order:
            combined_order[desc] = None

    # Step 2: Assign sort order based on the combined_order
    description_order = {desc: idx for idx, desc in enumerate(combined_order.keys())}
    # Step 3: Merge df with relevant_existing_rows
    merged_data = pd.concat([relevant_existing_rows, df]).drop_duplicates(
        subset=["Symbol", "Normalized_Description"], keep="last"
    )
    # Step 4: Sort the merged data using the custom order
    merged_data["sort_order"] = merged_data["Normalized_Description"].map(description_order)
    merged_data = merged_data.sort_values(by=["Symbol", "sort_order"]).drop(
        columns=["sort_order", "Normalized_Description"]
    )

    # Step 6: Remove old rows for the symbols being updated
    symbols_to_update = df["Symbol"].unique()
    existing_data[section] = existing_data[section][~existing_data[section]["Symbol"].isin(symbols_to_update)]

    # Step 7: Append the merged data back to existing_data[section]
    existing_data[section] = pd.concat([existing_data[section], merged_data], ignore_index=True)

    # Step 8: Reindex columns and fill missing values with NaN
    existing_data[section] = existing_data[section].reindex(
        columns=["Symbol", "Company", "Description", "COACode"]
        + sorted(set(merged_data.columns) - {"Symbol", "Company", "Description", "COACode"}),
        fill_value=pd.NA,
    )
    fixed_columns = ["Symbol", "Company", "Description", "COACode"]
    date_columns = [
        col
        for col in existing_data[section].columns
        if col not in fixed_columns and re.match(r"^[A-Za-z]{3} \d{4}$", col)
    ]
    # Sort the date columns in ascending order by date
    sorted_date_columns = sorted(date_columns, key=lambda x: datetime.strptime(x, "%b %Y"))

    # Reorder the columns
    existing_data[section] = existing_data[section][fixed_columns + sorted_date_columns]

    # Step 9: Save the updated section to file
    sections = ["Balance Sheet", "Profit & Loss", "Quarterly Results", "Cash Flows", "Shareholding Pattern"]
    section_files = {
        section: f"{get_dynamic_config().get('datapath')}/{section.lower().replace(' ', '_')}.rds"
        for section in sections
    }
    file_path = section_files[section]
    saveRDS(existing_data[section], os.path.expanduser(file_path))

    get_bootlick_logger().log_debug(f"Section '{section}' saved with updated data for symbols: {symbols_to_update}", {"section": section, "symbols_to_update": symbols_to_update, "function": "save_section_data"})


def get_symbol_list(proxy_source, proxy_user, proxy_pass, api_key, driver_path):
    driver = get_session_or_driver(
        url_to_test="https://screener.in",
        get_session=False,
        headless=False,
        proxy_source=proxy_source,
        api_key=api_key,
        proxy_user=proxy_user,
        proxy_password=proxy_pass,
        webdriver_path=driver_path,
    )
    try:
        symbols = []
        # Open Screener.in login page
        driver.get("https://www.screener.in/login/")

        # Wait for the login form to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

        # Enter username
        username_field = driver.find_element(By.NAME, "username")
        username_field.send_keys(get_dynamic_config()["credentials"]["username"])  # Replace with your email
        time.sleep(5)
        # Enter password
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(get_dynamic_config()["credentials"]["password"])  # Replace with your password
        time.sleep(4)
        # Submit the login form
        # The above code is using the `send_keys` method to simulate pressing the "Return" key on the
        # `password_field` element. This is commonly used to submit a form or trigger an action after
        # entering a password or other input.
        password_field.send_keys(Keys.RETURN)

        # Wait for the login to complete
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "top-navigation")))

        get_bootlick_logger().log_info("Login successful!", {"function": "get_symbol_list"})

        # Perform further actions after login
        # For example, navigate to a specific page
        time.sleep(2)
        base_url = "https://www.screener.in/results/latest/?sme=nse"
        p = 0
        try:
            while True:
                get_bootlick_logger().log_info(log_data_consumed(driver), {"function": "get_symbol_list"})
                p = p + 1
                driver.get(f"{base_url}&p={p}")
                # driver.get("https://www.screener.in/results/latest/?")
                time.sleep(5)  # Wait for the page to load
                if driver.current_url == "https://www.screener.in/results/latest/":
                    get_bootlick_logger().log_info("Reached the base page after exhausting all pages. Stopping pagination.", {"function": "get_symbol_list"})
                    break
                # Wait for the page to fully load after clicking the link
                WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
                get_bootlick_logger().log_info(f"Page fully loaded. {base_url}&p={p}", {"base_url": base_url, "page": p, "function": "get_symbol_list"})

                page_source = driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")
                company_links = soup.find_all("a", href=lambda href: href and "/company/" in href)
                for link in company_links:
                    href = link["href"]
                    # Extract the symbol (e.g., "VIJIFIN") from the href
                    symbol = href.split("/")[2]  # The symbol is the third part of the href
                    symbols.append(symbol)
        except Exception as e:
            get_bootlick_logger().log_error(f"Error while fetching symbols on page {p}", e, {"page": p, "function": "get_symbol_list"})

        # Remove duplicates (if any) and print the symbols
        symbols = list(set(symbols))

    finally:
        # Close the browser
        driver.quit()
        return symbols


def get_fiscal_period(symbol, end_date):
    fiscal_exception = FiscalYearException.get(symbol, {})
    for date, month in sorted(fiscal_exception.items(), reverse=True):
        if end_date >= date:
            fiscal_month = month
            break
    else:
        fiscal_month = "March"

    if fiscal_month == "March":
        next_fiscal_year_end = dt.datetime(end_date.year, 3, 31)
        if end_date > next_fiscal_year_end:
            next_fiscal_year_end = dt.datetime(end_date.year + 1, 3, 31)
    elif fiscal_month == "January":
        next_fiscal_year_end = dt.datetime(end_date.year, 1, 31)
        if end_date > next_fiscal_year_end:
            next_fiscal_year_end = dt.datetime(end_date.year + 1, 1, 31)
    elif fiscal_month == "June":
        next_fiscal_year_end = dt.datetime(end_date.year, 6, 30)
        if end_date > next_fiscal_year_end:
            next_fiscal_year_end = dt.datetime(end_date.year + 1, 6, 30)
    elif fiscal_month == "September":
        next_fiscal_year_end = dt.datetime(end_date.year, 9, 30)
        if end_date > next_fiscal_year_end:
            next_fiscal_year_end = dt.datetime(end_date.year + 1, 9, 30)
    elif fiscal_month == "December":
        next_fiscal_year_end = dt.datetime(end_date.year, 12, 31)
        if end_date > next_fiscal_year_end:
            next_fiscal_year_end = dt.datetime(end_date.year + 1, 12, 31)

    prior_fiscal_year_end = next_fiscal_year_end - dt.timedelta(days=365)

    return prior_fiscal_year_end, next_fiscal_year_end


# Function to get the last calendar date of a month
def get_last_day_of_month(date):
    next_month = date.replace(day=28) + dt.timedelta(days=4)  # this will never fail
    return next_month - dt.timedelta(days=next_month.day)


def reformat_balance_sheet(df):
    columns_to_process = df.columns[4:]

    # Precompute end dates for all columns
    end_dates = [get_last_day_of_month(dt.datetime.strptime(column, "%b %Y")) for column in columns_to_process]

    # Precompute fiscal periods and other metadata for all rows
    fiscal_data = [get_fiscal_period(symbol, end_date) for symbol in df["Symbol"] for end_date in end_dates]
    period_types = [
        "Annual" if end_date.month == next_fiscal.month else "Interim"
        for (_, next_fiscal), end_date in zip(fiscal_data, end_dates * len(df))
    ]
    period_lengths = [
        (end_date - prior_fiscal).days // 30 for (prior_fiscal, _), end_date in zip(fiscal_data, end_dates * len(df))
    ]
    fiscal_period_numbers = [
        float("nan") if period_type == "Annual" else period_length // 3
        for period_type, period_length in zip(period_types, period_lengths)
    ]

    # Assign metadata directly to the rows of the DataFrame
    metadata = {
        "EndDate": np.tile(end_dates, len(df)),
        "FiscalYear": [next_fiscal.year for _, next_fiscal in fiscal_data],
        "FiscalPeriodNumber": fiscal_period_numbers,
        "PeriodType": period_types,
        "PeriodLength": period_lengths,
        "StatementType": ["BAL"] * len(fiscal_data),
    }

    # Repeat original data for each column to process
    repeated_data = pd.DataFrame(
        {
            "Symbol": df["Symbol"].repeat(len(columns_to_process)).values,
            "Description": df["Description"].repeat(len(columns_to_process)).values,
            "COACode": df["COACode"].repeat(len(columns_to_process)).values,
            "Value": df[columns_to_process].values.flatten(),
        }
    )

    # Combine repeated data and metadata
    reformatted_data = pd.concat([repeated_data.reset_index(drop=True), pd.DataFrame(metadata)], axis=1)
    reformatted_data = reformatted_data.sort_values(by="EndDate", ascending=True).reset_index(drop=True)
    reformatted_data = reformatted_data.dropna(subset=["Value"])
    return reformatted_data


def reformat_pnl(df, statement_type):
    columns_to_process = df.columns[4:]

    # Precompute end dates and fiscal years for all columns
    end_dates = []
    for column in columns_to_process:
        match = re.search(r"[A-Za-z]{3} \d{4}", column)
        if match:
            end_dates.append(get_last_day_of_month(dt.datetime.strptime(match.group(), "%b %Y")))
        else:
            get_bootlick_logger().log_warning(f"Invalid column format: {column}", {"column": column, "function": "reformat_balance_sheet"})
    fiscal_years = [get_fiscal_period(symbol, end_date)[1].year for symbol in df["Symbol"] for end_date in end_dates]

    # Assign metadata directly to the rows of the DataFrame
    metadata = {
        "EndDate": np.tile(end_dates, len(df)),
        "FiscalYear": fiscal_years,
        "FiscalPeriodNumber": [float("nan")] * len(fiscal_years),
        "PeriodType": ["Annual"] * len(fiscal_years),
        "PeriodLength": [12] * len(fiscal_years),
        "StatementType": [statement_type] * len(fiscal_years),
    }

    # Repeat original data for each column to process
    repeated_data = pd.DataFrame(
        {
            "Symbol": df["Symbol"].repeat(len(columns_to_process)).values,
            "Description": df["Description"].repeat(len(columns_to_process)).values,
            "COACode": df["COACode"].repeat(len(columns_to_process)).values,
            "Value": df[columns_to_process].values.flatten(),
        }
    )

    # Combine repeated data and metadata
    reformatted_data = pd.concat([repeated_data.reset_index(drop=True), pd.DataFrame(metadata)], axis=1)
    reformatted_data = reformatted_data.sort_values(by="EndDate", ascending=True).reset_index(drop=True)
    reformatted_data = reformatted_data.dropna(subset=["Value"])

    return reformatted_data


def reformat_quarterly_pnl(df):
    columns_to_process = df.columns[4:]

    # Precompute end dates, fiscal periods, and other metadata for all columns
    end_dates = [get_last_day_of_month(dt.datetime.strptime(column, "%b %Y")) for column in columns_to_process]
    fiscal_data = [get_fiscal_period(symbol, end_date) for symbol in df["Symbol"] for end_date in end_dates]
    period_lengths = [
        (end_date - prior_fiscal).days // 30 for (prior_fiscal, _), end_date in zip(fiscal_data, end_dates * len(df))
    ]
    fiscal_period_numbers = [period_length // 3 for period_length in period_lengths]

    # Assign metadata directly to the rows of the DataFrame
    metadata = {
        "EndDate": np.tile(end_dates, len(df)),
        "FiscalYear": [next_fiscal.year for _, next_fiscal in fiscal_data],
        "FiscalPeriodNumber": fiscal_period_numbers,
        "PeriodType": ["Interim"] * len(fiscal_data),
        "PeriodLength": 3,
        "StatementType": ["INC"] * len(fiscal_data),
    }

    # Repeat original data for each column to process
    repeated_data = pd.DataFrame(
        {
            "Symbol": df["Symbol"].repeat(len(columns_to_process)).values,
            "Description": df["Description"].repeat(len(columns_to_process)).values,
            "COACode": df["COACode"].repeat(len(columns_to_process)).values,
            "Value": df[columns_to_process].values.flatten(),
        }
    )

    # Combine repeated data and metadata
    reformatted_data = pd.concat([repeated_data.reset_index(drop=True), pd.DataFrame(metadata)], axis=1)
    reformatted_data = reformatted_data.sort_values(by="EndDate", ascending=True).reset_index(drop=True)
    reformatted_data = reformatted_data.dropna(subset=["Value"])

    return reformatted_data


def reformat_cash_flows(df):
    return reformat_pnl(df, "CAS")


def reformat_shareholding(df):
    columns_to_process = df.columns[4:]

    # Precompute end dates for all columns
    end_dates = [get_last_day_of_month(dt.datetime.strptime(column, "%b %Y")) for column in columns_to_process]

    # Precompute fiscal periods and other metadata for all rows
    period_lengths = [12] * len(end_dates)  # Assuming shareholding data is annual
    fiscal_period_numbers = [float("nan")] * len(end_dates)  # No fiscal period numbers for shareholding
    period_types = ["Annual"] * len(end_dates)  # Assuming shareholding data is annual

    # Assign metadata directly to the rows of the DataFrame
    metadata = {
        "EndDate": np.tile(end_dates, len(df)),
        "FiscalYear": [end_date.year for end_date in end_dates] * len(df),
        "FiscalPeriodNumber": fiscal_period_numbers * len(df),
        "PeriodType": period_types * len(df),
        "PeriodLength": period_lengths * len(df),
        "StatementType": ["HLD"] * len(end_dates) * len(df),
    }

    # Repeat original data for each column to process
    repeated_data = pd.DataFrame(
        {
            "Symbol": df["Symbol"].repeat(len(columns_to_process)).values,
            "Description": df["Description"].repeat(len(columns_to_process)).values,
            "COACode": [""] * len(df) * len(columns_to_process),  # COACode is empty for shareholding
            "Value": df[columns_to_process].values.flatten(),
        }
    )

    # Combine repeated data and metadata
    reformatted_data = pd.concat([repeated_data.reset_index(drop=True), pd.DataFrame(metadata)], axis=1)
    reformatted_data = reformatted_data.sort_values(by="EndDate", ascending=True).reset_index(drop=True)

    # Drop rows where the 'Value' column is NaN
    reformatted_data = reformatted_data.dropna(subset=["Value"])

    return reformatted_data


# Load fiscal year exceptions
fiscal_year_exceptions = get_dynamic_config().get("fiscal_year_exceptions", {})
FiscalYearException = {
    symbol: {dt.datetime.strptime(date, "%Y-%m-%d"): month for date, month in dates.items()}
    for symbol, dates in fiscal_year_exceptions.items()
}
