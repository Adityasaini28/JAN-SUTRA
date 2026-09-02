from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42

DISTRICTS = [
    ("Ahmedabad", "Gujarat", 8200000, 78.5, 82.1, 79.2, 85.0),
    ("Surat", "Gujarat", 6500000, 80.2, 79.4, 81.0, 78.0),
    ("Vadodara", "Gujarat", 3200000, 75.0, 77.0, 76.5, 72.0),
    ("Rajkot", "Gujarat", 2100000, 71.2, 73.5, 68.0, 69.5),
    ("Bhavnagar", "Gujarat", 1800000, 64.0, 68.0, 62.0, 60.0),
    ("Kutch", "Gujarat", 2100000, 58.0, 59.0, 48.0, 51.0),
    ("Mumbai Suburban", "Maharashtra", 9300000, 68.0, 85.0, 82.0, 89.0),
    ("Pune", "Maharashtra", 7400000, 74.0, 83.0, 79.0, 78.0),
    ("Nagpur", "Maharashtra", 4600000, 70.5, 75.0, 74.0, 71.0),
    ("Nashik", "Maharashtra", 3900000, 66.0, 71.0, 70.0, 64.0),
    ("Aurangabad", "Maharashtra", 3700000, 61.0, 65.0, 58.0, 57.0),
    ("Nanded", "Maharashtra", 3300000, 52.0, 58.0, 51.0, 48.0),
    ("Jaipur", "Rajasthan", 6600000, 72.0, 76.0, 66.0, 73.0),
    ("Jodhpur", "Rajasthan", 3600000, 65.0, 68.0, 54.0, 61.0),
    ("Kota", "Rajasthan", 1950000, 69.0, 72.0, 68.0, 64.0),
    ("Udaipur", "Rajasthan", 3100000, 63.0, 64.0, 61.0, 56.0),
    ("Bikaner", "Rajasthan", 2400000, 58.0, 61.0, 45.0, 50.0),
    ("Barmer", "Rajasthan", 2600000, 51.0, 52.0, 39.0, 42.0),
    ("Bengaluru Urban", "Karnataka", 9600000, 62.0, 84.0, 75.0, 79.0),
    ("Mysuru", "Karnataka", 3000000, 74.0, 76.0, 78.0, 72.0),
    ("Dharwad", "Karnataka", 1850000, 68.0, 73.0, 69.0, 67.0),
    ("Belagavi", "Karnataka", 4800000, 63.0, 67.0, 65.0, 60.0),
    ("Kalaburagi", "Karnataka", 2600000, 54.0, 58.0, 52.0, 50.0),
    ("Raichur", "Karnataka", 1900000, 50.0, 54.0, 48.0, 45.0),
    ("Indore", "Madhya Pradesh", 3300000, 78.0, 77.0, 74.0, 75.0),
    ("Bhopal", "Madhya Pradesh", 2400000, 73.0, 75.0, 71.0, 72.0),
    ("Gwalior", "Madhya Pradesh", 2050000, 64.0, 68.0, 63.0, 62.0),
    ("Jabalpur", "Madhya Pradesh", 2460000, 65.0, 70.0, 66.0, 61.0),
    ("Ujjain", "Madhya Pradesh", 2000000, 62.0, 66.0, 59.0, 58.0),
    ("Rewa", "Madhya Pradesh", 2360000, 53.0, 57.0, 49.0, 47.0),
    ("Lucknow", "Uttar Pradesh", 4600000, 71.0, 79.0, 72.0, 74.0),
    ("Varanasi", "Uttar Pradesh", 3700000, 66.0, 74.0, 68.0, 68.0),
    ("Kanpur Nagar", "Uttar Pradesh", 4500000, 63.0, 71.0, 66.0, 66.0),
    ("Prayagraj", "Uttar Pradesh", 5900000, 60.0, 67.0, 61.0, 60.0),
    ("Gorakhpur", "Uttar Pradesh", 4400000, 57.0, 65.0, 58.0, 55.0),
    ("Jhansi", "Uttar Pradesh", 2000000, 55.0, 62.0, 52.0, 52.0),
]

ISSUES = {
    "Public Transport": [
        ("Delay/Frequency", "The bus frequency on a major route is poor, with long morning waits.", "Negative"),
        ("Crowding", "Peak-hour buses are heavily overcrowded and uncomfortable.", "Negative"),
        ("Connectivity", "Last-mile connectivity from the main transit hub is limited.", "Negative"),
        ("Service Quality", "Public transport has become cleaner and more reliable recently.", "Positive"),
        ("Fare/Cost", "Fare changes have increased the cost of commuting.", "Negative"),
        ("Schedule", "Vehicles do not consistently follow the published timetable.", "Negative"),
    ],
    "Healthcare": [
        ("Doctor Availability", "The public clinic has long queues because too few doctors are available.", "Negative"),
        ("Waiting Time", "Registration and consultation took several hours.", "Negative"),
        ("Medicine Stock", "Common medicines were unavailable at the facility.", "Negative"),
        ("Service Quality", "Doctors and nursing staff provided attentive care.", "Positive"),
        ("Diagnostics", "Diagnostic reporting took longer than expected.", "Negative"),
        ("Facility Quality", "The facility was clean and well maintained.", "Positive"),
    ],
    "Roads": [
        ("Potholes", "Potholes on the arterial road are creating safety concerns.", "Negative"),
        ("Lighting", "Street lighting is inadequate on several road segments.", "Negative"),
        ("Maintenance", "Road resurfacing has improved travel quality.", "Positive"),
        ("Erosion", "Road surfaces deteriorated after heavy rainfall.", "Negative"),
        ("Traffic Safety", "Road markings and speed-control measures need improvement.", "Negative"),
        ("Work Quality", "Recent patchwork repairs have started deteriorating.", "Negative"),
    ],
    "Water Supply": [
        ("Supply Frequency", "Water supply is intermittent and pressure is low.", "Negative"),
        ("Water Purity", "Residents reported concerns about water quality.", "Negative"),
        ("Tap Connectivity", "Piped water supply is regular and convenient.", "Positive"),
        ("Tanker Dependency", "Dependence on private tankers is increasing household costs.", "Negative"),
        ("Leakage", "A pipeline leak near a residential area has remained unresolved.", "Negative"),
    ],
    "Electricity": [
        ("Outages", "Unscheduled power cuts are affecting households and small businesses.", "Negative"),
        ("Voltage", "Voltage fluctuations have damaged electrical appliances.", "Negative"),
        ("Reliability", "Electricity supply has been stable and uninterrupted.", "Positive"),
        ("Billing", "Billing errors are creating avoidable grievance cases.", "Negative"),
        ("Transformer", "Transformer failures are frequent during high-demand periods.", "Negative"),
    ],
    "Sanitation": [
        ("Waste Collection", "Garbage collection has become irregular in residential lanes.", "Negative"),
        ("Drainage", "Drainage overflow is creating hygiene and mosquito concerns.", "Negative"),
        ("Door-to-Door", "Door-to-door collection is working reliably in this area.", "Positive"),
        ("Public Toilets", "Public toilets are not consistently functional.", "Negative"),
        ("Sweeping", "Street sweeping is concentrated on main roads.", "Negative"),
    ],
    "Employment": [
        ("Job Creation", "Lack of local opportunities is pushing young workers to migrate.", "Negative"),
        ("Training", "A local skills programme helped participants find work.", "Positive"),
        ("Recruitment", "Recruitment opportunities for technical roles are limited.", "Negative"),
        ("Wage Delay", "Payments under public employment programmes are delayed.", "Negative"),
    ],
    "Public Safety": [
        ("Patrolling", "Residents want stronger night-time patrolling on vulnerable routes.", "Negative"),
        ("Crime Rate", "Recent theft incidents have increased safety concerns.", "Negative"),
        ("Emergency Response", "Emergency response was prompt when assistance was requested.", "Positive"),
        ("Traffic Control", "Traffic management has improved safety during peak hours.", "Positive"),
    ],
    "Education": [
        ("Infrastructure", "The school lacks adequate laboratory and digital facilities.", "Negative"),
        ("Digital Education", "Digital classroom access has improved learning conditions.", "Positive"),
        ("Staffing", "Teacher vacancies are affecting continuity of instruction.", "Negative"),
        ("Attendance", "Teacher attendance and student participation have improved.", "Positive"),
    ],
    "Digital Government Services": [
        ("Server Downtime", "The online service portal frequently becomes unavailable.", "Negative"),
        ("CSC Efficiency", "The service centre completed the application quickly.", "Positive"),
        ("Grievance Redressal", "Digital complaints are not always resolved within expected timelines.", "Negative"),
        ("Payment Gateway", "Online payment for government services is fast and transparent.", "Positive"),
    ],
}

ISSUE_WEIGHTS = {
    "Public Transport": .18, "Healthcare": .16, "Roads": .16, "Water Supply": .12,
    "Electricity": .10, "Sanitation": .08, "Employment": .06, "Public Safety": .05,
    "Education": .05, "Digital Government Services": .04,
}

def generate(output_dir="data", n_records=12500):
    rng = np.random.default_rng(SEED)
    random.seed(SEED)
    out = pd.Path if False else None
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    district_rows = []
    for d, state, pop, road, health, water, transport in DISTRICTS:
        district_rows.append({
            "district": d, "state": state, "population": pop,
            "road_quality_index": road, "healthcare_access_index": health,
            "water_access_index": water, "public_transport_index": transport
        })
    ind = pd.DataFrame(district_rows)
    ind.to_csv(Path(output_dir) / "district_indicators.csv", index=False)

    districts = ind["district"].tolist()
    issue_names = list(ISSUE_WEIGHTS)
    start = datetime(2026, 1, 1)
    rows = []

    for i in range(1, n_records + 1):
        dist = random.choice(districts)
        meta = ind[ind["district"] == dist].iloc[0]
        issue = random.choices(issue_names, weights=list(ISSUE_WEIGHTS.values()))[0]
        dt = start + timedelta(days=random.randint(0, 240))

        # Synthetic mechanism: weaker service index + selected seasonal shock -> more negative feedback.
        index_map = {
            "Public Transport": meta["public_transport_index"],
            "Healthcare": meta["healthcare_access_index"],
            "Water Supply": meta["water_access_index"],
            "Roads": meta["road_quality_index"],
            "Electricity": 0.7 * meta["road_quality_index"] + 0.3 * meta["water_access_index"],
        }
        service_idx = index_map.get(issue, 70.0)
        bias = np.clip((100 - service_idx) / 100 + rng.normal(0, .10), .08, .85)

        if issue in {"Roads", "Public Transport"} and dt.month in {6, 7, 8}:
            bias = min(.9, bias + .18)
        if issue == "Water Supply" and dt.month in {4, 5, 6}:
            bias = min(.9, bias + .15)

        roll = random.random()
        choices = ISSUES[issue]
        neg = [x for x in choices if x[2] == "Negative"]
        pos = [x for x in choices if x[2] == "Positive"]
        if roll < bias:
            item = random.choice(neg)
        else:
            item = random.choice(pos if pos else choices)

        service_type, comment, sentiment = item
        satisfaction = (
            random.choice([1, 2, 3]) if sentiment == "Negative"
            else random.choice([3, 4, 5]) if sentiment == "Positive"
            else 3
        )
        rows.append({
            "feedback_id": f"FB-2026-{i:06d}",
            "district": dist, "state": meta["state"],
            "survey_date": dt.strftime("%Y-%m-%d"),
            "issue_category": issue, "service_type": service_type,
            "sentiment": sentiment, "satisfaction_score": satisfaction,
            "comment": comment,
        })

    feedback = pd.DataFrame(rows)

    # Deliberate quality defects for the audit pipeline to demonstrate.
    feedback.loc[12, "sentiment"] = "Unknown"
    feedback.loc[45, "satisfaction_score"] = np.nan
    feedback.loc[88, "district"] = "Unspecified District"
    feedback = pd.concat([feedback, feedback.iloc[[100, 200]]], ignore_index=True)
    feedback.to_csv(Path(output_dir) / "citizen_feedback_raw.csv", index=False)

    return feedback, ind
