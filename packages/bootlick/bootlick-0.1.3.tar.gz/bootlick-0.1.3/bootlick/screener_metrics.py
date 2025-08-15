import pandas as pd
from chameli.interactions import readRDS, saveRDS
from chameli.dateutils import valid_datetime
from ohlcutils.data import load_symbol
from ohlcutils.indicators import calculate_beta
import yaml
import numpy as np
import re
from .config import get_config

# Import bootlick_logger lazily to avoid circular import
def get_bootlick_logger():
    """Get bootlick_logger instance to avoid circular imports."""
    from . import bootlick_logger
    return bootlick_logger

# lookback = 0 => latest rolling 1 year
# lookback >= 1 => latest annual, prior annual etc

# Load the COA code mappings from the YAML file


def get_dynamic_config():
    return get_config()


def is_base_metric(metric):
    """
    Check if the metric exists in the values of specific keys in coa_mappings.
    """
    valid_categories = ["Balance Sheet", "Profit & Loss", "Quarterly Results", "Cash Flows"]
    for category in valid_categories:
        if metric in get_dynamic_config().get(category, {}).values():
            return True
    return False


def is_indicator(indicator):
    """
    Check if the indicator exists in the keys of custom_indicators.
    """
    valid_categories = ["custom_indicators"]
    for category in valid_categories:
        if indicator in get_dynamic_config().get(category, {}).keys():
            return True
    return False


def expand_coa_codes(metric, coa_mappings):
    """
    Recursively expand add_coa_codes and sub_coa_codes for a given metric,
    handling multipliers for metrics.

    Args:
        metric (str): The metric to expand.
        coa_mappings (dict): The COA mappings from the YAML file.

    Returns:
        tuple: (expanded_add_coa_codes, expanded_sub_coa_codes)
               Each is a dictionary where keys are metrics and values are multipliers.
    """
    # Get the initial COA codes for the metric
    coa_codes = get_dynamic_config().get(metric, {"add_coa_codes": set(), "sub_coa_codes": set()})
    add_coa_codes = set(coa_codes["add_coa_codes"])
    sub_coa_codes = set(coa_codes["sub_coa_codes"])

    # Initialize expanded dictionaries with multipliers
    expanded_add_coa_codes = {}
    expanded_sub_coa_codes = {}

    # Helper function to parse multipliers
    def parse_multiplier(code):
        if "*" in code:
            multiplier, base_metric = [part.strip() for part in code.split("*")]
            return float(multiplier), base_metric
        return 1.0, code  # Default multiplier is 1.0

    # Expand add_coa_codes
    for code in add_coa_codes:
        multiplier, base_metric = parse_multiplier(code)
        if not is_base_metric(base_metric):  # If the base metric is a dependent metric
            # Recursively expand the dependent metric
            dep_add, dep_sub = expand_coa_codes(base_metric, get_dynamic_config())
            for dep_metric, dep_multiplier in dep_add.items():
                expanded_add_coa_codes[dep_metric] = (
                    expanded_add_coa_codes.get(dep_metric, 0) + dep_multiplier * multiplier
                )
            for dep_metric, dep_multiplier in dep_sub.items():
                expanded_sub_coa_codes[dep_metric] = (
                    expanded_sub_coa_codes.get(dep_metric, 0) + dep_multiplier * multiplier
                )
        else:
            # If it's a direct COA code, add it to the expanded set
            expanded_add_coa_codes[base_metric] = expanded_add_coa_codes.get(base_metric, 0) + multiplier

    # Expand sub_coa_codes
    for code in sub_coa_codes:
        multiplier, base_metric = parse_multiplier(code)
        if not is_base_metric(base_metric):  # If the base metric is a dependent metric
            # Recursively expand the dependent metric
            dep_add, dep_sub = expand_coa_codes(base_metric, get_dynamic_config())
            for dep_metric, dep_multiplier in dep_add.items():
                expanded_sub_coa_codes[dep_metric] = (
                    expanded_sub_coa_codes.get(dep_metric, 0) + dep_multiplier * multiplier
                )
            for dep_metric, dep_multiplier in dep_sub.items():
                expanded_add_coa_codes[dep_metric] = (
                    expanded_add_coa_codes.get(dep_metric, 0) + dep_multiplier * multiplier
                )
        else:
            # If it's a direct COA code, add it to the expanded set
            expanded_sub_coa_codes[base_metric] = expanded_sub_coa_codes.get(base_metric, 0) + multiplier

    return expanded_add_coa_codes, expanded_sub_coa_codes


def calculate_metrics(df, symbol, metric, lookback=0, target_date=float("nan")):
    def get_latest_by_index(temp_df, metric, target_date):
        add_coa_codes, sub_coa_codes = expand_coa_codes(metric, get_dynamic_config())
        add_values = []
        sub_values = []
        result = 0
        if not pd.isna(target_date):
            target_date = valid_datetime(target_date)[0]
            if np.datetime64(target_date) in temp_df[(temp_df["PeriodType"] == "Annual")]["EndDate"].values:
                periodType = "Annual"
            else:
                periodType = "Interim"
            add_values = (
                temp_df[(temp_df["PeriodType"] == periodType) & (temp_df["COACode"].isin(add_coa_codes.keys()))]
                .groupby("EndDate", group_keys=False)
                .apply(
                    lambda group: sum(
                        add_coa_codes[code] * group.loc[group["COACode"] == code, "Value"].sum()
                        for code in add_coa_codes
                        if code in group["COACode"].values
                    )
                )
                .sort_index(ascending=False)
            )
            sub_values = (
                temp_df[(temp_df["PeriodType"] == periodType) & (temp_df["COACode"].isin(sub_coa_codes.keys()))]
                .groupby("EndDate", group_keys=False)  # Explicitly set group_keys=False
                .apply(
                    lambda group: sum(
                        sub_coa_codes[code] * group.loc[group["COACode"] == code, "Value"].sum()
                        for code in sub_coa_codes
                        if code in group["COACode"].values
                    )
                )
                .sort_index(ascending=False)
            )

            if (len(add_values) > 0 and target_date in add_values.index) or (
                len(sub_values) > 0 and target_date in sub_values.index
            ):
                result = add_values.get(target_date, 0) - sub_values.get(target_date, 0)
            else:
                result = 0
        return result, target_date

    def get_latest_by_rolling_period(temp_df, metric, target_date):
        """
        Calculate the latest rolling period value for a given metric.

        Args:
            temp_df (pd.DataFrame): Filtered DataFrame containing relevant data.
            metric (str): The metric to calculate.
            lookback (int): Lookback period (only valid for lookback == 0 in this function).

        Returns:
            tuple: (calculated value, target_date)
        """
        add_coa_codes, sub_coa_codes = expand_coa_codes(metric, get_dynamic_config())
        result = 0
        # Use the specified target_date directly if provided
        if not pd.isna(target_date):
            temp_df = temp_df[temp_df["PeriodType"] == "Interim"]
            last_date = (
                temp_df[(temp_df["EndDate"] <= target_date)]["EndDate"]
                .drop_duplicates()
                .sort_values(ascending=False)
                .tolist()
            )
            if len(last_date) < 4 or last_date[0] != target_date:
                return 0, target_date  # Not enough data to calculate

            # Calculate the sum of add_coa_codes with multipliers
            sum_codes = [code for code in add_coa_codes.keys() if not code.endswith("_D")]
            avg_codes = [code for code in add_coa_codes.keys() if code.endswith("_D")]
            sum_values = (
                temp_df[(temp_df["EndDate"].isin(last_date[:4])) & (temp_df["COACode"].isin(sum_codes))]
                .groupby("COACode")["Value"]  # Select only the 'Value' column
                .sum()
            )

            # Calculate the average for COACodes that should be averaged
            avg_values = (
                temp_df[(temp_df["EndDate"].isin(last_date[:4])) & (temp_df["COACode"].isin(avg_codes))]
                .groupby("COACode")["Value"]  # Select only the 'Value' column
                .mean()
            )

            # Combine the results into a single Series
            add_values = pd.concat([sum_values, avg_values])
            add_result = sum(add_coa_codes[code] * add_values.get(code, 0) for code in add_coa_codes)

            # Calculate the sum of sub_coa_codes with multipliers
            sum_codes = [code for code in sub_coa_codes.keys() if not code.endswith("_D")]
            avg_codes = [code for code in sub_coa_codes.keys() if code.endswith("_D")]
            sum_values = (
                temp_df[(temp_df["EndDate"].isin(last_date[:4])) & (temp_df["COACode"].isin(sum_codes))]
                .groupby("COACode")["Value"]  # Select only the 'Value' column
                .sum()
            )

            # Calculate the average for COACodes that should be averaged
            avg_values = (
                temp_df[(temp_df["EndDate"].isin(last_date[:4])) & (temp_df["COACode"].isin(avg_codes))]
                .groupby("COACode")["Value"]  # Select only the 'Value' column
                .mean()
            )
            sub_values = pd.concat([sum_values, avg_values])
            sub_result = sum(sub_coa_codes[code] * sub_values.get(code, 0) for code in sub_coa_codes)
            result = add_result - sub_result
        return result, target_date

    add_coa_codes, sub_coa_codes = expand_coa_codes(metric, get_dynamic_config())
    if isinstance(target_date, pd.Timestamp):
        target_date = target_date.to_pydatetime()
    if pd.isna(target_date):
        # Get all annual dates for the symbol, sorted in descending order
        if lookback == 0:
            interim_dates = (
                df[(df["Symbol"] == symbol) & (df["PeriodType"] == "Interim")]["EndDate"]
                .drop_duplicates()
                .sort_values(ascending=False)
                .tolist()
            )
            if len(interim_dates) > 0:
                target_date = interim_dates[0]
            else:
                return 0, float("nan")
        else:
            annual_dates = (
                df[(df["Symbol"] == symbol) & (df["PeriodType"] == "Annual")]["EndDate"]
                .drop_duplicates()
                .sort_values(ascending=False)
                .tolist()
            )
        if lookback - 1 < len(annual_dates):
            target_date = annual_dates[lookback - 1]
        else:
            return 0, float("nan")  # Not enough data for the given lookback

    # Ensure target_date is a valid datetime
    target_date = valid_datetime(target_date)[0]

    filtered_df = df[(df["Symbol"] == symbol) & (df["COACode"].isin(add_coa_codes | sub_coa_codes))]
    if lookback == 0:
        profit_loss_coa = set(get_dynamic_config().get("Profit & Loss", {}).values())
        cash_flows_coa = set(get_dynamic_config().get("Cash Flows", {}).values())

        period_metric = bool(
            set(add_coa_codes.keys()).intersection(profit_loss_coa)
            or set(add_coa_codes.keys()).intersection(cash_flows_coa)
            or set(sub_coa_codes.keys()).intersection(profit_loss_coa)
            or set(sub_coa_codes.keys()).intersection(cash_flows_coa)
        )
        if period_metric:
            return get_latest_by_rolling_period(filtered_df, metric, target_date)
        else:
            return get_latest_by_index(filtered_df, metric, target_date)
    else:
        return get_latest_by_index(filtered_df, metric, target_date)


# Define custom functions
def avg(metric_values, lookback):
    """Calculate the average of the last `lookback` values."""
    if len(metric_values) < lookback:
        return float("nan")  # Not enough data
    return np.mean(metric_values[:lookback])


def sd(metric_values, lookback):
    """Calculate the standard deviation of the last `lookback` values."""
    if len(metric_values) < lookback:
        return float("nan")  # Not enough data
    return np.std(metric_values[:lookback])


def diff(metric_values, lookback):
    """Calculate the difference of the last `lookback` values."""
    if len(metric_values) < lookback:
        return float("nan")  # Not enough data
    return metric_values[0] - metric_values[lookback - 1]


def diff_percent(metric_values, lookback):
    """Calculate the percentage difference of the last `lookback` values."""
    if len(metric_values) < lookback:
        return float("nan")  # Not enough data
    return (metric_values[0] - metric_values[lookback - 1]) / metric_values[lookback - 1]


def is_float(value):
    try:
        float(value)  # Try converting to float
        return True
    except ValueError:
        return False


def extract_metrics(formula):
    """
    Extract metrics from a formula, handling nested functions like avg() or sd().

    Args:
        formula (str): The formula string to parse.

    Returns:
        list: A list of unique metrics extracted from the formula.
    """
    # Regular expression to match metrics, including nested functions like avg() or sd()
    pattern = r"[a-zA-Z_]+\([a-zA-Z0-9_, ]+\)|[a-zA-Z_]+"

    # Find all matches in the formula
    matches = re.findall(pattern, formula)

    # Remove duplicates and return the cleaned list
    return list(set(matches))


def calculate_custom_indicator(df, symbol, indicator_name, lookback=0, target_date=float("nan")):
    """
    Calculate a custom indicator based on a formula defined in a YAML file.

    Args:
        df (pd.DataFrame): Financial data containing COACode, Value, EndDate, PeriodType, Symbol, etc.
        symbol (str): The company's symbol to calculate the indicator for.
        indicator_name (str): The name of the custom indicator (e.g., 'roce', 'fcf_yield').
        lookback (int): Lookback period for the metrics.
        target_date (float or datetime): Optional target date for the calculation.

    Returns:
        tuple: (calculated value, target_date) for the specified indicator.
    """
    # Load custom indicators from the YAML file
    custom_indicators = get_dynamic_config().get("custom_indicators", {})

    # Get the formula for the specified indicator
    indicator = custom_indicators.get(indicator_name)
    if not indicator:
        get_bootlick_logger().log_error(f"Indicator '{indicator_name}' is not defined in the YAML file.", ValueError(f"Indicator '{indicator_name}' is not defined in the YAML file."), {
            "indicator_name": indicator_name,
            "function": "calculate_custom_indicator"
        })
        raise ValueError(f"Indicator '{indicator_name}' is not defined in the YAML file.")

    formula = indicator["formula"]

    # Extract the metrics used in the formula
    metrics = extract_metrics(formula)

    # Calculate each metric using the calculate_metrics function
    metric_values = {}
    target_dates = {}

    # Get all annual dates for the symbol if target_date is provided
    if not pd.isna(target_date):
        target_date = valid_datetime(target_date)[0]

        # Filter annual dates to include only those less than or equal to target_date
        annual_dates = (
            df[(df["Symbol"] == symbol) & (df["PeriodType"] == "Annual") & (df["EndDate"] <= target_date)]["EndDate"]
            .drop_duplicates()
            .sort_values(ascending=False)
            .tolist()
        )
    else:
        annual_dates = (
            df[(df["Symbol"] == symbol) & (df["PeriodType"] == "Annual")]["EndDate"]
            .drop_duplicates()
            .sort_values(ascending=False)
            .tolist()
        )
        if lookback - 1 < len(annual_dates):
            annual_dates = annual_dates[lookback - 1 :]
            target_date = annual_dates[0]
        else:
            return 0, float("nan")

    for metric in metrics:
        if metric_values.get(metric) is not None:
            pass
        if is_float(metric):
            pass
        else:
            try:
                # Attempt to parse the metric as a formula (e.g., avg(metric, lookback))
                base_metric, lookback_period = metric[metric.index("(") + 1 : metric.rindex(")")].split(",")
                lookback_period = int(lookback_period.strip())
                values = []

                for i in range(lookback_period):
                    # Use target_dates if available
                    if i < len(annual_dates):
                        current_target_date = annual_dates[i]
                    else:
                        current_target_date = float("nan")

                    if is_indicator(base_metric):
                        value, metric_target_date = calculate_custom_indicator(
                            df, symbol, base_metric, lookback + i, current_target_date
                        )
                    else:
                        value, metric_target_date = calculate_metrics(
                            df, symbol, base_metric, lookback + i, current_target_date
                        )
                    if pd.isna(value):
                        return 0, metric_target_date  # Return 0 if any metric is invalid
                    values.append(value)

                # Determine the operation based on the metric prefix
                if metric.startswith("avg("):
                    metric_values[metric] = avg(values, lookback_period)
                elif metric.startswith("sd("):
                    metric_values[metric] = sd(values, lookback_period)
                elif metric.startswith("diff("):
                    metric_values[metric] = diff(values, lookback_period)
                elif metric.startswith("diff_percent("):
                    metric_values[metric] = diff_percent(values, lookback_period)
                else:
                    get_bootlick_logger().log_error(f"Unsupported formula: {metric}", ValueError(f"Unsupported formula: {metric}"), {
                        "metric": metric,
                        "function": "calculate_custom_indicator"
                    })
                    raise ValueError(f"Unsupported formula: {metric}")
            except (ValueError, IndexError):
                # If parsing fails, check if it's an indicator
                if is_indicator(metric):
                    value, metric_target_date = calculate_custom_indicator(df, symbol, metric, lookback, target_date)
                    if pd.isna(value):
                        return 0, metric_target_date  # Return 0 if any metric is invalid
                    metric_values[metric] = value
                    target_dates[metric] = metric_target_date
                else:
                    # Handle regular metrics
                    value, metric_target_date = calculate_metrics(df, symbol, metric, lookback, target_date)
                    if pd.isna(value):
                        return 0, metric_target_date  # Return 0 if any metric is invalid
                    metric_values[metric] = value
                    target_dates[metric] = metric_target_date

    # Ensure all target dates are the same
    unique_target_dates = set(target_dates.values())
    if len(unique_target_dates) > 1:
        return 0, float("nan")  # Return 0 if target dates are not the same

    # Preprocess the formula to replace avg() and sd() with the actual key in metric_values
    for metric in list(metric_values.keys()):  # Use list() to create a copy of the keys
        match = re.search(r"([a-zA-Z_]+)\(([^,]+),\s*([0-9]+)\)", metric)
        if match:
            formula = formula.replace(metric, str(metric_values[metric]))

    # Evaluate the formula using the calculated metric values
    try:
        result = eval(formula, {}, metric_values)
    except ZeroDivisionError:
        result = 0  # Handle division by zero gracefully

    # Return the result and the common target date
    return result, unique_target_dates.pop() if unique_target_dates else float("nan")


def format_in_lakh_crore(value):
    """
    Format a number with comma separators for lakhs and crores.
    Args:
        value (float or int): The number to format.
    Returns:
        str: The formatted string with comma separators.
    """
    if pd.isna(value) or not isinstance(value, (int, float)):
        return value  # Return as is for NaN or non-numeric values
    return f"{value:,.2f}"  # Format with commas and 2 decimal places


# Apply formatting to the DataFrame
def pretty_print_df(df):
    """
    Pretty print the DataFrame with formatted numbers.
    Args:
        df (pd.DataFrame): The DataFrame to format.
    Returns:
        pd.DataFrame: A DataFrame with formatted numbers.
    """
    formatted_df = df.copy()
    # Apply formatting only to numeric columns
    for col in formatted_df.columns[1:]:  # Skip the 'Category' column
        formatted_df[col] = formatted_df[col].apply(format_in_lakh_crore)
    return formatted_df


def beta(symbol, end_date):
    md = load_symbol(
        symbol + "_STK___", start_time=valid_datetime(end_date)[0] - pd.DateOffset(years=1), end_time=end_date
    )
    md_bench = load_symbol(
        "NSENIFTY_IND___", start_time=valid_datetime(end_date)[0] - pd.DateOffset(years=1), end_time=end_date
    )
    beta = calculate_beta(md, md_bench, window=len(md) - 1)
    return beta.iloc[-1].item()


def estimate_ir(md, symbol, lookback, annual_dates, log=False):
    """
    Estimate the internal reinvestment rate (IR).

    Args:
        md (pd.DataFrame): Financial dataset.
        symbol (str): Stock symbol.
        lookback (int): Lookback period.
        annual_dates (list): List of annual dates sorted from most recent to oldest.
        log (bool): Print logs if True.

    Returns:
        float: IR
    """
    ic_deltas, nopats, ext_funds = [], [], []

    # Use up to 3 most recent periods, but fewer if less data is available
    n_periods = min(3, len(annual_dates))
    for offset in range(n_periods - 1, -1, -1):
        current_td = annual_dates[offset] if offset < len(annual_dates) else float("nan")

        ic_growth, _ = calculate_custom_indicator(md, symbol, "ic_growth_abs", lookback + offset, current_td)
        nop, _ = calculate_custom_indicator(md, symbol, "nopat", lookback + offset, current_td)
        ext, _ = calculate_metrics(md, symbol, "ext_funds_raised", lookback + offset, current_td)

        if any(pd.isna(x) for x in [ic_growth, nop, ext]):
            continue

        ic_deltas.append(ic_growth)
        nopats.append(nop)
        ext_funds.append(0.5 * max(ext, 0))  # Mid-year fund application assumption

    # Cumulative values
    cum_ic_deltas = np.cumsum(ic_deltas)
    cum_nopats = np.cumsum(nopats)
    cum_ext_funds = np.cumsum(ext_funds)
    cum_ir = cum_ic_deltas / (cum_ext_funds + cum_nopats)
    ir = min(cum_ir[-1], 1) if len(cum_ir) > 0 else 0.3
    ir = 0.3 if ir < 0 else ir  # Ensure IR is not less than 0.3
    return ir


def intrinsic_pe(
    md,
    symbol,
    lookback=1,
    target_date=float("nan"),
    terminal_g=0.06,
    rf=0.06,
    g=[],
    ir=None,
    roic=None,
    nopat=None,
    log=False,
):
    """
    The intrinsic_pe function calculates the intrinsic price-to-earnings (P/E) ratio for a
    given company symbol based on its financial data. It uses a discounted cash flow (DCF)
    approach, incorporating free cash flows (FCFs), terminal value, and weighted average
    cost of capital (WACC). The function dynamically adjusts growth rates and calculates the
    intrinsic P/E ratio based on the company's net operating profit after tax (NOPAT).

     Args:

        md (pd.DataFrame): The financial data containing columns such as COACode, Value, EndDate, PeriodType, Symbol, etc.

        symbol (str): The company's symbol for which the intrinsic P/E ratio is calculated.

        lookback (int, default=1): The lookback period for the metrics.
        lookback=0: Uses the latest rolling 1-year data.
        lookback>=1: Uses the latest annual data, prior annual data, etc.

        target_date (float or datetime, default=float("nan")): The optional target date for the calculation. If not provided, the function determines the target date based on the lookback period.

        terminal_g (float, default=0.06): The terminal growth rate used in the terminal value calculation.

        rf (float, default=0.06): The risk-free rate (default is 6%).

        g (list or float, default=[]): The growth rate(s) for the free cash flows.

        If a single value is provided, it is used for all iterations.
        If a list is provided, it specifies the growth rate for each iteration.
        ir (float, default=None): The investment rate. If not provided, it is calculated dynamically.

        roic (float, default=None): The return on invested capital. If not provided, it is calculated dynamically.

        nopat (float, default=None): The net operating profit after tax. If not provided, it is calculated dynamically.

        log (bool, default=False): If True, logs intermediate calculations for debugging purposes.



     Returns:
         tuple: (calculated value, target_date, nopat) for the intrinsic P/E ratio.
    """

    if not pd.isna(target_date):
        target_date = valid_datetime(target_date)[0]
        annual_dates = (
            md[(md["Symbol"] == symbol) & (md["PeriodType"] == "Annual") & (md["EndDate"] <= target_date)]["EndDate"]
            .drop_duplicates()
            .sort_values(ascending=False)
            .tolist()
        )
    else:
        annual_dates = (
            md[(md["Symbol"] == symbol) & (md["PeriodType"] == "Annual")]["EndDate"]
            .drop_duplicates()
            .sort_values(ascending=False)
            .tolist()
        )
        if lookback - 1 < len(annual_dates):
            annual_dates = annual_dates[lookback - 1 :]
            target_date = annual_dates[0]
        else:
            return 0, float("nan"), {}

    # Get NOPAT for the target year
    nopat_calc, target_date = calculate_custom_indicator(md, symbol, "nopat", lookback, target_date)
    if pd.isna(target_date):
        return 0, target_date, {}
    if nopat is None:
        nopat = nopat_calc
    nopat_seed = nopat

    # Calculate Beta
    beta_symbol = beta(symbol, target_date)

    # Estimate ROIC as 3-year average if not provided
    if roic is None:
        roic_values = []
        for i in range(3):
            if i < len(annual_dates):
                current_target = annual_dates[i]
            else:
                current_target = float("nan")
            value, _ = calculate_custom_indicator(md, symbol, "roic", lookback + i, current_target)
            roic_values.append(value)
        roic = avg(roic_values, 3)

    # ----------- Estimate IR and α using Regression ----------- #
    if not g:
        ir = estimate_ir(md, symbol, lookback, annual_dates, log=log)
        g = [ir * roic]

    if g:
        ir = [g_i / roic for g_i in g]

    if log:
        get_bootlick_logger().log_info("--- Estimation Summary ---", {
            "symbol": symbol,
            "roic": roic,
            "ir": ir,
            "growth_rate": g,
            "target_date": target_date,
            "function": "intrinsic_pe"
        })

    # Equity and Debt
    equity = calculate_metrics(md, symbol, "equity", lookback, target_date)[0]
    debt = calculate_metrics(md, symbol, "debt", lookback, target_date)[0]

    # Cost of Equity (CAPM) and Debt
    re = rf + beta_symbol * 0.065
    rd = min(re - 0.02, rf + 0.04)

    # WACC
    total_cap = equity + debt
    wacc = (debt / total_cap) * rd + (equity / total_cap) * re

    if log:
        get_bootlick_logger().log_info(f"WACC: {wacc:.4f}, Re: {re:.4f}, Rd: {rd:.4f}", {
            "symbol": symbol,
            "wacc": wacc,
            "re": re,
            "rd": rd,
            "function": "intrinsic_pe"
        })

    # --- FCF and DCF Calculation ---
    fcf_values = []
    year = 1
    iter_count = 5 if len(g) == 1 else len(g)
    g = g * iter_count if len(g) == 1 else g

    for i in range(iter_count):
        nopat = nopat * (1 + g[i])
        fcf = nopat * (1 - g[i] / roic)  # = NOPAT * (1 - IR)
        fcf_values.append(fcf / ((1 + wacc) ** year))
        year += 1

    # Terminal value
    terminal_value = (nopat * (1 - terminal_g / roic)) / (wacc - terminal_g)
    terminal_value_pv = terminal_value / ((1 + wacc) ** (year - 1))

    EV = sum(fcf_values) + terminal_value_pv
    equity_value = EV - debt
    intrinsic_pe = equity_value / nopat_seed

    # Return result
    return (
        intrinsic_pe,
        target_date,
        {
            "nopat": nopat_seed,
            "wacc": wacc,
            "roic": roic,
            "cf_growth": g,
            "ir": ir,
        },
    )


def operating_view(md, symbol, years=4):
    """
    Generate an operational view table with invested capital and sources of capital.

    Business Logic:
    - Constructs a table showing the evolution of key operational and financial metrics for a company over the last N years.
    - For each year (lookback), computes values for a set of categories, including working capital, gross block, depreciation, invested capital, goodwill, CWIP, non-operating assets, debt, equity, and liabilities.
    - Some rows are direct metrics, while others are calculated as sums or differences of other metrics (e.g., "Invested capital, excluding goodwill" = invested_capital - goodwill).
    - Handles empty rows for visual separation.
    - Appends custom indicators (roce, roic, oper_investment_rate, cap_investment_rate, g) as additional rows, calculated for each lookback period.
    - Appends "intrinsic_pe" as the last row, showing the intrinsic price-to-earnings ratio for each lookback.
    - The resulting DataFrame has columns for each year (or lookback), and rows for each metric/category, with values filled in or calculated as appropriate.
    - The columns are sorted chronologically, and the first column is always "Category".

    Args:
        md (pd.DataFrame): The financial data.
        symbol (str): The company's symbol.
        years (int): Number of lookback years to include.

    Returns:
        pd.DataFrame: A DataFrame containing the operational view table.
    """
    # Define the categories and their corresponding metrics
    categories = [
        ("Working capital", "working_capital"),
        ("Property, plant, and equipment, gross", "gross_block"),
        ("Gross depreciation", "depreciation"),
        ("Invested capital, excluding goodwill", None),  # Calculated as a diff
        ("Goodwill and acquired intangibles", "intangibles"),
        ("Invested capital, including goodwill", None),  # Calculated as a sum
        ("", None),  # Empty row
        ("CWIP", "cwip"),
        ("Other non-operating assets", None),
        ("Total funds invested", None),  # Calculated as a sum
        ("", None),  # Empty row
        ("Short-term debt", "st_borrowings"),
        ("Long-term debt", "lt_borrowings"),
        ("Lease liabilities", "lease_liabilities"),
        ("Debt and debt equivalents", None),  # Calculated as a sum
        ("Preference capital", "preference_capital"),
        ("Shareholders' equity", "equity"),
        ("Non operating non fin liabilities", "non_operating_non_financial_liabilities"),
        ("Total source of funds", None),  # Calculated as a sum
    ]

    # Initialize the data dictionary
    data = {"Category": [category[0] for category in categories]}

    # Get all Annual EndDates for the symbol, sorted in descending order
    annual_dates = (
        md[(md["Symbol"] == symbol) & (md["PeriodType"] == "Annual")]["EndDate"]
        .drop_duplicates()
        .sort_values(ascending=False)
        .tolist()
    )

    if not annual_dates:
        get_bootlick_logger().log_error(f"No Annual data available for symbol '{symbol}'.", ValueError(f"No Annual data available for symbol '{symbol}'."), {
            "symbol": symbol,
            "function": "operating_view"
        })
        raise ValueError(f"No Annual data available for symbol '{symbol}'.")

    # Initialize the latest target_date
    target_date = annual_dates[0]

    # Populate lookback columns dynamically
    column_headers = []  # Store column headers for sorting later
    invested_capital_values = []
    g_act_values = []
    for lookback in range(1, years + 1):  # Lookback periods 1 to 4
        column_values = []

        # Adjust target_date for the current lookback
        if lookback > 1:
            if lookback - 1 < len(annual_dates):
                target_date = annual_dates[lookback - 1]
            else:
                target_date = float("nan")  # No more Annual dates available

        for category, metric in categories:
            if metric is None:
                # Handle calculated rows
                if category == "Invested capital, excluding goodwill":
                    invested_capital, _ = calculate_metrics(md, symbol, "invested_capital", lookback, target_date)
                    goodwill, _ = calculate_metrics(md, symbol, "intangibles", lookback, target_date)
                    column_values.append(
                        invested_capital - goodwill if invested_capital is not None and goodwill is not None else None
                    )
                elif category == "Invested capital, including goodwill":
                    excl_goodwill = column_values[categories.index(("Invested capital, excluding goodwill", None))]
                    goodwill = column_values[categories.index(("Goodwill and acquired intangibles", "intangibles"))]
                    invested_capital_incl_goodwill = (
                        excl_goodwill + goodwill if excl_goodwill is not None and goodwill is not None else None
                    )
                    column_values.append(invested_capital_incl_goodwill)
                    invested_capital_values.append(invested_capital_incl_goodwill)
                elif category == "Other non-operating assets":
                    cwip = column_values[categories.index(("CWIP", "cwip"))]
                    non_oper_assets, _ = calculate_metrics(md, symbol, "non_operating_assets", lookback, target_date)
                    column_values.append(
                        non_oper_assets - cwip if non_oper_assets is not None and cwip is not None else None
                    )
                elif category == "Total funds invested":
                    ic = column_values[categories.index(("Invested capital, including goodwill", None))]
                    cwip = column_values[categories.index(("CWIP", "cwip"))]
                    other_non_oper_assets = column_values[categories.index((("Other non-operating assets", None)))]
                    depreciation = column_values[categories.index((("Gross depreciation", "depreciation")))]

                    total = (
                        ic + cwip + other_non_oper_assets + depreciation
                        if ic is not None
                        and cwip is not None
                        and other_non_oper_assets is not None
                        and depreciation is not None
                        else None
                    )
                    column_values.append(total)
                elif category == "Total source of funds":
                    tot_debt = column_values[categories.index(("Debt and debt equivalents", None))]
                    equity = (
                        column_values[categories.index(("Shareholders' equity", "equity"))]
                        + column_values[categories.index(("Preference capital", "preference_capital"))]
                    )
                    non_oper_liab = column_values[
                        categories.index(
                            ("Non operating non fin liabilities", "non_operating_non_financial_liabilities")
                        )
                    ]
                    total = (
                        tot_debt + equity + non_oper_liab
                        if tot_debt is not None and equity is not None and non_oper_liab is not None
                        else None
                    )
                    column_values.append(total)
                elif category == "Debt and debt equivalents":
                    st_debt = column_values[categories.index(("Short-term debt", "st_borrowings"))]
                    lt_debt = column_values[categories.index(("Long-term debt", "lt_borrowings"))]
                    lease_liab = column_values[categories.index(("Lease liabilities", "lease_liabilities"))]
                    column_values.append(
                        st_debt + lt_debt + lease_liab
                        if st_debt is not None and lt_debt is not None and lease_liab is not None
                        else None
                    )
                else:
                    column_values.append(None)  # Empty rows
            else:
                # Calculate the metric value
                value, _ = calculate_metrics(md, symbol, metric, lookback, target_date)
                column_values.append(value if not pd.isna(value) else None)

        # Add the column to the data dictionary with the target_date as the header
        column_header = f"{target_date.strftime('%Y-%m-%d')}" if not pd.isna(target_date) else f"Lookback {lookback}"
        column_headers.append(column_header)
        data[column_header] = column_values

    # Append custom indicators as rows
    custom_indicators = ["ic_growth", "roce", "roic", "oper_investment_rate", "cap_investment_rate", "g"]
    for indicator in custom_indicators:
        row_values = [indicator]  # Start with the indicator name as the category
        for lookback in range(1, years + 1):  # Lookback periods 1 to 4
            if lookback - 1 < len(annual_dates):
                target_date = annual_dates[lookback - 1]
            else:
                target_date = float("nan")
            value, _ = calculate_custom_indicator(md, symbol, indicator, lookback, target_date)
            if indicator in ["oper_investment_rate", "cap_investment_rate"]:
                value = -1 * value  # Multiply by -1 for these indicators
            row_values.append(round(value, 4) if not pd.isna(value) else None)
        # Append the row to the data dictionary
        for key, value in zip(data.keys(), row_values):
            data[key].append(value)

    # Append intrinsic_pe as the last row
    intrinsic_pe_row = ["intrinsic_pe_2%_tg"]  # Start with the indicator name as the category
    for lookback in range(1, years + 1):  # Lookback periods 1 to 4
        if lookback - 1 < len(annual_dates):
            target_date = annual_dates[lookback - 1]
        else:
            target_date = float("nan")
        value, _, _ = intrinsic_pe(md, symbol, lookback, target_date=target_date)
        intrinsic_pe_row.append(round(value, 2) if not pd.isna(value) else None)
    # Append the row to the data dictionary
    for key, value in zip(data.keys(), intrinsic_pe_row):
        data[key].append(value)

    intrinsic_pe_row = ["intrinsic_pe_6%_tg"]  # Start with the indicator name as the category
    for lookback in range(1, years + 1):  # Lookback periods 1 to 4
        if lookback - 1 < len(annual_dates):
            target_date = annual_dates[lookback - 1]
        else:
            target_date = float("nan")
        value, _, _ = intrinsic_pe(md, symbol, lookback, target_date=target_date, terminal_g=0.06)
        intrinsic_pe_row.append(round(value, 2) if not pd.isna(value) else None)
    # Append the row to the data dictionary
    for key, value in zip(data.keys(), intrinsic_pe_row):
        data[key].append(value)

    # Convert the data dictionary to a DataFrame
    df = pd.DataFrame(data)

    # Sort columns by date, ensuring the last column corresponds to the highest date
    sorted_columns = ["Category"] + sorted(column_headers, key=lambda x: pd.to_datetime(x, errors="coerce"))
    df = df[sorted_columns]

    return df
