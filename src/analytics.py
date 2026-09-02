import numpy as np
import pandas as pd


# ============================================================
# TREND ANALYSIS
# ============================================================

class TrendAnalyzer:

    def __init__(self, feedback):
        self.df = feedback.copy()

    def monthly(self, issue=None, district=None):

        d = self.df.copy()

        if issue is not None:
            d = d[d["issue_category"] == issue]

        if district is not None:
            d = d[d["district"] == district]

        if d.empty:
            return pd.DataFrame(
                columns=[
                    "month",
                    "feedback_volume",
                    "negative_pct",
                    "avg_satisfaction",
                ]
            )

        out = (
            d.groupby("month")
            .agg(
                feedback_volume=("feedback_id", "count"),
                negative_pct=(
                    "sentiment",
                    lambda x: (
                        x.eq("Negative").mean() * 100
                    )
                ),
                avg_satisfaction=(
                    "satisfaction_score",
                    "mean",
                ),
            )
            .reset_index()
            .sort_values("month")
        )

        return out

    def metrics(
        self,
        issue,
        district=None,
    ):

        ts = self.monthly(
            issue,
            district,
        )

        if len(ts) < 3:

            return {
                "status": "Insufficient history",
                "delta_pp": 0.0,
                "z_score": 0.0,
                "months_observed": len(ts),
            }

        current = float(
            ts.iloc[-1]["negative_pct"]
        )

        previous = float(
            ts.iloc[-2]["negative_pct"]
        )

        history = ts.iloc[:-1]["negative_pct"]

        historical_mean = float(
            history.mean()
        )

        historical_std = float(
            history.std(ddof=1)
        )

        if historical_std > 1e-9:

            z_score = (
                current - historical_mean
            ) / historical_std

        else:

            z_score = 0.0

        delta_pp = (
            current - previous
        )

        if (
            z_score >= 1.75
            and delta_pp >= 5
        ):

            status = "Escalating"

        elif delta_pp <= -5:

            status = "Improving"

        else:

            status = (
                "Stable / normal fluctuation"
            )

        return {
            "status": status,
            "current_neg_pct": round(
                current,
                1,
            ),
            "previous_neg_pct": round(
                previous,
                1,
            ),
            "delta_pp": round(
                delta_pp,
                1,
            ),
            "historical_mean": round(
                historical_mean,
                1,
            ),
            "historical_std": round(
                historical_std,
                1,
            ),
            "z_score": round(
                z_score,
                2,
            ),
            "months_observed": len(ts),
        }


# ============================================================
# EVIDENCE ENGINE
# ============================================================

class EvidenceEngine:

    INDEX_MAP = {
        "Public Transport": "public_transport_index",
        "Healthcare": "healthcare_access_index",
        "Roads": "road_quality_index",
        "Water Supply": "water_access_index",
    }

    def __init__(
        self,
        feedback,
        indicators,
    ):

        self.feedback = feedback.copy()
        self.indicators = indicators.copy()

    def evaluate(self, issue):

        d = self.feedback[
            self.feedback["issue_category"] == issue
        ].copy()

        if d.empty:
            return []

        evidence = []

        # ----------------------------------------------------
        # 1. COMPLAINT CONCENTRATION
        # ----------------------------------------------------

        negative = d[
            d["sentiment"] == "Negative"
        ]

        if not negative.empty:

            driver_share = (
                negative["service_type"]
                .value_counts(
                    normalize=True
                )
                .mul(100)
                .head(3)
            )

            for driver, share in driver_share.items():

                evidence.append(
                    {
                        "hypothesis": (
                            f"Dissatisfaction is concentrated "
                            f"around {driver}."
                        ),
                        "evidence_type": (
                            "Complaint concentration"
                        ),
                        "support": round(
                            float(share),
                            1,
                        ),
                        "interpretation": (
                            f"{share:.1f}% of negative "
                            f"{issue} feedback references "
                            f"{driver}."
                        ),
                        "status": "Observed",
                    }
                )

        # ----------------------------------------------------
        # 2. DISTRICT-LEVEL ASSOCIATION
        # ----------------------------------------------------

        target = self.INDEX_MAP.get(issue)

        if target is None:

            evidence.append(
                {
                    "hypothesis": (
                        "Operational capacity cannot be "
                        "tested with the available indicator."
                    ),
                    "evidence_type": (
                        "Evidence gap"
                    ),
                    "support": None,
                    "interpretation": (
                        f"No district-level {issue.lower()} "
                        "indicator is available in the demo data."
                    ),
                    "status": "Insufficient data",
                }
            )

            return evidence

        district_rates = (
            d.groupby("district")["sentiment"]
            .apply(
                lambda x:
                x.eq("Negative").mean() * 100
            )
            .rename("negative_rate")
            .reset_index()
        )

        merged = district_rates.merge(
            self.indicators[
                ["district", target]
            ],
            on="district",
            how="inner",
        )

        if len(merged) >= 5:

            correlation = merged[
                "negative_rate"
            ].corr(
                merged[target]
            )

            if pd.notna(correlation):

                evidence.append(
                    {
                        "hypothesis": (
                            f"Lower {issue.lower()} "
                            "service capacity is associated "
                            "with higher dissatisfaction."
                        ),
                        "evidence_type": (
                            "District-level association"
                        ),
                        "support": round(
                            abs(float(correlation))
                            * 100,
                            1,
                        ),
                        "interpretation": (
                            f"Pearson r={correlation:.2f}. "
                            "This is an association across "
                            "districts, not evidence of causation."
                        ),
                        "status": (
                            "Observed association"
                        ),
                    }
                )

        else:

            evidence.append(
                {
                    "hypothesis": (
                        "District-level association "
                        "cannot yet be evaluated."
                    ),
                    "evidence_type": (
                        "Evidence gap"
                    ),
                    "support": None,
                    "interpretation": (
                        "Fewer than five matched districts "
                        "are available for the association test."
                    ),
                    "status": (
                        "Insufficient data"
                    ),
                }
            )

        return evidence


# ============================================================
# PRIORITY SCORING
# ============================================================

class PriorityScorer:

    WEIGHTS = {
        "prevalence": 0.25,
        "negative_sentiment": 0.25,
        "trend": 0.20,
        "exposure": 0.15,
        "evidence": 0.15,
    }

    @classmethod
    def score_issue(
        cls,
        feedback,
        indicators,
        issue,
    ):

        d = feedback[
            feedback["issue_category"] == issue
        ].copy()

        if d.empty:

            return {
                "issue_category": issue,
                "priority_score": 0.0,
                "prevalence": 0.0,
                "negative_sentiment": 0.0,
                "trend": 0.0,
                "exposure": 0.0,
                "evidence": 0.0,
            }

        total_feedback = max(
            len(feedback),
            1,
        )

        # ----------------------------------------------------
        # PREVALENCE
        # ----------------------------------------------------

        prevalence_raw = (
            len(d) / total_feedback
        )

        prevalence = min(
            100.0,
            prevalence_raw / 0.25 * 100,
        )

        # ----------------------------------------------------
        # NEGATIVE SENTIMENT
        # ----------------------------------------------------

        negative_sentiment = (
            d["sentiment"]
            .eq("Negative")
            .mean()
            * 100
        )

        # ----------------------------------------------------
        # TREND
        # ----------------------------------------------------

        trend_metrics = TrendAnalyzer(
            feedback
        ).metrics(issue)

        trend_score = min(
            100.0,
            max(
                0.0,
                50
                + trend_metrics["delta_pp"] * 3
                + max(
                    0,
                    trend_metrics["z_score"],
                ) * 5,
            ),
        )

        # ----------------------------------------------------
        # EXPOSURE
        # ----------------------------------------------------

        affected_districts = (
            d["district"]
            .dropna()
            .unique()
            .tolist()
        )

        affected_population = indicators[
            indicators["district"].isin(
                affected_districts
            )
        ]["population"].sum()

        total_population = indicators[
            "population"
        ].sum()

        exposure = min(
            100.0,
            affected_population
            / max(
                total_population,
                1,
            )
            * 100,
        )

        # ----------------------------------------------------
        # EVIDENCE
        # ----------------------------------------------------

        negative_count = int(
            d["sentiment"]
            .eq("Negative")
            .sum()
        )

        if negative_count >= 100:
            evidence = 80.0
        elif negative_count >= 50:
            evidence = 65.0
        elif negative_count >= 20:
            evidence = 50.0
        elif negative_count >= 10:
            evidence = 35.0
        else:
            evidence = 20.0

        # ----------------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------------

        final_score = (
            cls.WEIGHTS["prevalence"]
            * prevalence
            +
            cls.WEIGHTS["negative_sentiment"]
            * negative_sentiment
            +
            cls.WEIGHTS["trend"]
            * trend_score
            +
            cls.WEIGHTS["exposure"]
            * exposure
            +
            cls.WEIGHTS["evidence"]
            * evidence
        )

        return {
            "issue_category": issue,
            "priority_score": round(
                final_score,
                1,
            ),
            "prevalence": round(
                prevalence,
                1,
            ),
            "negative_sentiment": round(
                negative_sentiment,
                1,
            ),
            "trend": round(
                trend_score,
                1,
            ),
            "exposure": round(
                exposure,
                1,
            ),
            "evidence": round(
                evidence,
                1,
            ),
        }

    @classmethod
    def score_all(
        cls,
        feedback,
        indicators,
    ):

        issues = sorted(
            feedback[
                "issue_category"
            ]
            .dropna()
            .unique()
        )

        rows = [
            cls.score_issue(
                feedback,
                indicators,
                issue,
            )
            for issue in issues
        ]

        return (
            pd.DataFrame(rows)
            .sort_values(
                "priority_score",
                ascending=False,
            )
            .reset_index(drop=True)
        )