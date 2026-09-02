from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def build_pdf(path, district, issue, metrics, evidence, priority, action):
    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("JAN SUTRA | GOVERNANCE DECISION BRIEF", styles["Title"]),
        Paragraph(f"{district} • {issue} • {datetime.now().strftime('%d %B %Y')}", styles["Normal"]),
        Spacer(1, 12),
    ]

    table = Table([
        ["Priority", f"{priority:.1f}/100"],
        ["Negative sentiment", f"{metrics.get('current_neg_pct', 0):.1f}%"],
        ["MoM change", f"{metrics.get('delta_pp', 0):+.1f} pp"],
        ["Trend status", metrics.get("status", "N/A")],
        ["Evidence status", "Directional / non-causal"],
    ], colWidths=[160, 300])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), .5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.whitesmoke),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 7),
    ]))
    story.append(table)
    story.append(Spacer(1, 14))

    story += [
        Paragraph("1. What changed?", styles["Heading2"]),
        Paragraph(
            f"Negative sentiment is {metrics.get('current_neg_pct', 0):.1f}%, "
            f"with a month-on-month movement of {metrics.get('delta_pp', 0):+.1f} percentage points. "
            f"The statistical status is {metrics.get('status', 'N/A')}.",
            styles["BodyText"]
        ),
        Spacer(1, 8),
        Paragraph("2. What evidence supports the issue?", styles["Heading2"]),
    ]
    for e in evidence[:4]:
        story.append(Paragraph(
            f"<b>{e['evidence_type']}:</b> {e['interpretation']}",
            styles["BodyText"]
        ))
    story += [
        Spacer(1, 8),
        Paragraph("3. What should be investigated next?", styles["Heading2"]),
        Paragraph(
            f"<b>Proposed action:</b> {action['action']}<br/>"
            f"<b>Owner:</b> {action['owner']}<br/>"
            f"<b>Validation data:</b> {action['validation_data']}<br/>"
            f"<b>Success metric:</b> {action['success_metric']}",
            styles["BodyText"]
        ),
        Spacer(1, 8),
        Paragraph("4. Analytical caveat", styles["Heading2"]),
        Paragraph(
            "Citizen feedback identifies patterns and hypotheses; it does not establish administrative causation. "
            "Operational records and field verification are required before intervention decisions.",
            styles["BodyText"]
        ),
    ]
    doc.build(story)
