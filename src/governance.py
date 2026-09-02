DRIVER_TREES = {
    "Public Transport": {
        "root": "Access, reliability and commute quality",
        "branches": {
            "Availability & Coverage": ["Route coverage", "Feeder reach", "Service frequency"],
            "Reliability & Scheduling": ["Peak-hour delays", "Cancellations", "Fleet availability"],
            "Capacity & Safety": ["Overcrowding", "Women commuter safety", "Terminal quality"],
            "Affordability & Access": ["Fare burden", "Pass validation", "Concessions"],
        },
    },
    "Healthcare": {
        "root": "Access, capacity and service quality",
        "branches": {
            "Human Resources": ["Doctor availability", "Nursing capacity", "Absenteeism"],
            "Operational Friction": ["Registration wait", "OPD wait", "Operating hours"],
            "Diagnostics & Pharmacy": ["Medicine stock", "Equipment downtime", "Diagnostics"],
        },
    },
    "Roads": {
        "root": "Road quality and public safety",
        "branches": {
            "Surface Quality": ["Potholes", "Erosion", "Repair quality"],
            "Safety & Signage": ["Lighting", "Speed control", "Road markings"],
        },
    },
}

INTERVENTIONS = {
    "Public Transport": {
        "lever": "Service reliability",
        "action": "Audit peak-hour dispatch adherence and rebalance service frequency on high-complaint corridors.",
        "owner": "Transport authority / operating agency",
        "validation_data": "AVL/GPS logs, route schedules, cancellation records",
        "success_metric": "Median wait time and on-time departure rate",
    },
    "Healthcare": {
        "lever": "Capacity and patient flow",
        "action": "Review high-volume facilities for staffing gaps, queue bottlenecks and recurring medicine/diagnostic shortages.",
        "owner": "District health administration",
        "validation_data": "Attendance, OPD queue logs, stock registers",
        "success_metric": "Registration-to-consultation time and stock-out days",
    },
    "Roads": {
        "lever": "Maintenance prioritisation",
        "action": "Prioritise high-risk road segments for field verification and time-bound maintenance inspection.",
        "owner": "Roads / municipal engineering department",
        "validation_data": "Geo-tagged inspections, work orders, contractor records",
        "success_metric": "Verified defect closure time and repeat-defect rate",
    },
}

def driver_tree(issue):
    return DRIVER_TREES.get(issue, {
        "root": f"{issue} service delivery",
        "branches": {
            "Access & Coverage": ["Availability", "Reach", "Operating frequency"],
            "Delivery Quality": ["Wait times", "Reliability", "Citizen redressal"],
            "Infrastructure": ["Upkeep", "Capacity", "Technical downtime"],
        },
    })

def intervention(issue):
    return INTERVENTIONS.get(issue, {
        "lever": "Service delivery",
        "action": f"Conduct a departmental operational review of {issue} delivery using district-level evidence.",
        "owner": "Relevant district administration",
        "validation_data": "Departmental service records and field verification",
        "success_metric": "Service-level compliance and grievance resolution time",
    })
