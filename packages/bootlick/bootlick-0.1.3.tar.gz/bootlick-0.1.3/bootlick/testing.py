from bootlick import screener_metrics as sm
from bootlick.config import get_config
import pandas as pd
md = pd.read_parquet("/home/psharma/onedrive/data/financials/screener_fin.parquet")
out = sm.calculate_custom_indicator(md,"PDSL","roe",2)
print(out)
