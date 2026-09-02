import pandas as pd
from src.data_pipeline import DataCleaningPipeline

def test_cleaning_audit():
    raw = pd.DataFrame([
        {"feedback_id":"1","district":"A","survey_date":"2026-01-01","comment":"x","sentiment":"Unknown","satisfaction_score":None},
        {"feedback_id":"1","district":"A","survey_date":"2026-01-01","comment":"x","sentiment":"Unknown","satisfaction_score":None},
        {"feedback_id":"2","district":"B","survey_date":"2026-01-02","comment":"y","sentiment":"Positive","satisfaction_score":5},
    ])
    clean, audit = DataCleaningPipeline(raw, ["A","B"]).run()
    assert audit["duplicates_removed"] == 1
    assert audit["invalid_sentiments_standardized"] == 1
    assert audit["missing_satisfaction_imputed"] == 1
    assert len(clean) == 2
