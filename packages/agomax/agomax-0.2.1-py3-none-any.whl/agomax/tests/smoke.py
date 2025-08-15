from pathlib import Path
import pandas as pd
from agomax.core.detect import fit, score

BASE_DIR = Path(__file__).resolve().parents[1]
COLUMNS_YAML = BASE_DIR / "configs" / "columns.yaml"
RULES_YAML = BASE_DIR / "configs" / "rules.yaml"
DATA_DIR = BASE_DIR / "data"

base = pd.read_csv(DATA_DIR / "base.csv")
pack, base_full, base_feats = fit(base, str(COLUMNS_YAML))
res = score(pack, base, str(COLUMNS_YAML), str(RULES_YAML))
print({
    "rows": len(res),
    "anomalies": int(res["anomaly"].sum()),
})
