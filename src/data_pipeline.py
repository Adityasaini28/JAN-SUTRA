import pandas as pd
import numpy as np

class DataCleaningPipeline:
    VALID_SENTIMENTS = {"Positive", "Neutral", "Negative"}

    def __init__(self, df, valid_districts):
        self.raw = df.copy()
        self.valid_districts = set(valid_districts)

    def run(self):
        df = self.raw.copy()
        initial = len(df)

        duplicate_mask = df.duplicated(
            subset=["feedback_id", "district", "survey_date", "comment"], keep="first"
        )
        duplicates = int(duplicate_mask.sum())
        df = df.loc[~duplicate_mask].copy()

        df["survey_date"] = pd.to_datetime(df["survey_date"], errors="coerce")
        invalid_dates = int(df["survey_date"].isna().sum())
        df = df.dropna(subset=["survey_date"]).copy()

        invalid_district = ~df["district"].isin(self.valid_districts)
        unknown_districts = int(invalid_district.sum())
        df = df.loc[~invalid_district].copy()

        invalid_sentiment = ~df["sentiment"].isin(self.VALID_SENTIMENTS)
        invalid_sentiments = int(invalid_sentiment.sum())
        df.loc[invalid_sentiment, "sentiment"] = "Neutral"

        missing_satisfaction = int(df["satisfaction_score"].isna().sum())
        median_sat = float(df["satisfaction_score"].median())
        df["satisfaction_score"] = df["satisfaction_score"].fillna(median_sat)

        df["month"] = df["survey_date"].dt.to_period("M").astype(str)
        df["sentiment_score"] = df["sentiment"].map(
            {"Negative": -1.0, "Neutral": 0.0, "Positive": 1.0}
        )

        # Quality score measures observable data defects only; it is not model accuracy.
        defect_rate = (duplicates + invalid_dates + unknown_districts + invalid_sentiments) / max(initial, 1)
        quality_score = max(0.0, min(100.0, 100.0 - defect_rate * 100.0))

        audit = {
            "initial_records": initial,
            "cleaned_records": len(df),
            "duplicates_removed": duplicates,
            "invalid_dates_dropped": invalid_dates,
            "unknown_districts_dropped": unknown_districts,
            "invalid_sentiments_standardized": invalid_sentiments,
            "missing_satisfaction_imputed": missing_satisfaction,
            "data_quality_score": round(quality_score, 1),
        }
        return df.reset_index(drop=True), audit
