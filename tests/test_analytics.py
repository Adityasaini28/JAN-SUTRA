import pandas as pd
from src.analytics import TrendAnalyzer, PriorityScorer

def sample():
    rows=[]
    for month, neg in [("2026-01", False), ("2026-02", False), ("2026-03", True), ("2026-03", True)]:
        rows.append({
            "feedback_id": str(len(rows)), "district":"A", "issue_category":"Roads",
            "service_type":"Potholes", "sentiment":"Negative" if neg else "Positive",
            "satisfaction_score":1 if neg else 5, "month":month
        })
    return pd.DataFrame(rows)

def test_trend_has_delta():
    m=TrendAnalyzer(sample()).metrics("Roads")
    assert "delta_pp" in m
    assert m["months_observed"] == 3

def test_priority_bounded():
    d=sample()
    indicators=pd.DataFrame({"district":["A"],"population":[1000],"road_quality_index":[50]})
    r=PriorityScorer.score_issue(d, indicators, "Roads")
    assert 0 <= r["priority_score"] <= 100
