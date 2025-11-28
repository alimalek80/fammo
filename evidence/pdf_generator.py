from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.widgets.markers import makeMarker
from datetime import datetime
import os


def create_user_growth_chart(weekly_users):
    """Create a line chart for user growth"""
    drawing = Drawing(400, 200)
    
    chart = HorizontalLineChart()
    chart.x = 50
    chart.y = 30
    chart.height = 150
    chart.width = 330
    
    # Prepare data
    new_users_data = [week['new_users'] for week in weekly_users]
    total_users_data = [week['total_users'] for week in weekly_users]
    
    chart.data = [new_users_data, total_users_data]
    
    # Configure chart
    chart.lines[0].strokeColor = colors.HexColor('#3b82f6')  # Blue for new users
    chart.lines[0].strokeWidth = 2
    chart.lines[1].strokeColor = colors.HexColor('#10b981')  # Green for total users
    chart.lines[1].strokeWidth = 2
    
    # Add markers
    chart.lines[0].symbol = makeMarker('Circle')
    chart.lines[1].symbol = makeMarker('Circle')
    
    # Category names (week labels)
    chart.categoryAxis.categoryNames = [f"W{i+1}" for i in range(len(weekly_users))]
    chart.categoryAxis.labels.boxAnchor = 'n'
    chart.categoryAxis.labels.angle = 45
    chart.categoryAxis.labels.fontSize = 7
    
    # Value axis
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(total_users_data) * 1.1 if total_users_data else 100
    chart.valueAxis.valueStep = max(1, int(max(total_users_data) / 5)) if total_users_data else 20
    chart.valueAxis.labels.fontSize = 8
    
    # Legend
    legend = Legend()
    legend.x = 50
    legend.y = 10
    legend.fontName = 'Helvetica'
    legend.fontSize = 8
    legend.boxAnchor = 'sw'
    legend.columnMaximum = 2
    legend.strokeWidth = 1
    legend.strokeColor = colors.black
    legend.deltax = 75
    legend.deltay = 10
    legend.dx = 8
    legend.dy = 8
    legend.dxTextSpace = 5
    legend.colorNamePairs = [
        (colors.HexColor('#3b82f6'), 'New Users'),
        (colors.HexColor('#10b981'), 'Total Users')
    ]
    
    drawing.add(chart)
    drawing.add(legend)
    
    return drawing


def create_bar_chart(weekly_data, title, color_hex):
    """Create a bar chart for meal plans or health reports"""
    drawing = Drawing(400, 200)
    
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 30
    chart.height = 150
    chart.width = 330
    
    # Prepare data
    values = [week['meal_plans'] if 'meal_plans' in week else week['health_reports'] for week in weekly_data]
    
    chart.data = [values]
    
    # Configure bars
    chart.bars[0].fillColor = colors.HexColor(color_hex)
    chart.bars[0].strokeColor = colors.HexColor(color_hex)
    
    # Category names (week labels)
    chart.categoryAxis.categoryNames = [f"W{i+1}" for i in range(len(weekly_data))]
    chart.categoryAxis.labels.boxAnchor = 'n'
    chart.categoryAxis.labels.angle = 45
    chart.categoryAxis.labels.fontSize = 7
    
    # Value axis
    max_value = max(values) if values else 10
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max_value * 1.2
    chart.valueAxis.valueStep = max(1, int(max_value / 5))
    chart.valueAxis.labels.fontSize = 8
    
    drawing.add(chart)
    
    return drawing


def generate_evidence_pdf(context_data):
    """
    Generate a professional PDF report for FAMMO evidence
    """
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fammo_evidence_summary.pdf"'
    
    # Create the PDF object
    doc = SimpleDocTemplate(response, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=1*inch, bottomMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=4,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # ===== HEADER SECTION =====
    elements.append(Paragraph("EVIDENCE SUMMARY — FAMMO", title_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Header information
    current_date = datetime.now().strftime("%B %d, %Y")
    header_info = [
        f"<b>Version:</b> {current_date}",
        "<b>Prepared for:</b> Business Finland – Startup Permit Eligibility",
        "<b>Company:</b> FAMMO (AI-Powered Pet Nutrition Platform)",
        "<b>Website:</b> <link href='https://fammo.ai' color='blue'>https://fammo.ai</link>",
        "<b>Evidence Portal:</b> <link href='https://fammo.ai/en/evidence' color='blue'>https://fammo.ai/en/evidence</link>"
    ]
    
    for info in header_info:
        elements.append(Paragraph(info, subtitle_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Horizontal line
    elements.append(Paragraph("<hr/>", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # ===== SECTION 1: PLATFORM OVERVIEW =====
    elements.append(Paragraph("Section 1: Platform Overview", header_style))
    
    # Statistics table
    stats_data = [
        ['Metric', 'Count'],
        ['Total Registered Users', str(context_data.get('total_users', 0))],
        ['Total Dogs', str(context_data.get('total_dogs', 0))],
        ['Total Cats', str(context_data.get('total_cats', 0))],
        ['Total Pets', str(context_data.get('total_pets', 0))],
        ['AI Meal Plans Generated', str(context_data.get('total_meal_plans', 0))],
        ['AI Health Reports Generated', str(context_data.get('total_health_reports', 0))],
        ['Active Users (7 days)', str(context_data.get('active_users_7_days', 0))],
        ['Active Users (30 days)', str(context_data.get('active_users_30_days', 0))],
    ]
    
    stats_table = Table(stats_data, colWidths=[4.5*inch, 1.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # ===== SECTION 2: PRODUCT USAGE =====
    elements.append(Paragraph("Section 2: Product Usage Graphs", header_style))
    
    # Weekly User Growth - TABLE
    elements.append(Paragraph("<b>2.1 User Growth (Weekly)</b>", body_style))
    weekly_users = context_data.get('weekly_users', [])
    
    # Add the table first
    user_table_data = [['Week', 'New Users', 'Total Users', 'Growth %']]
    for week in weekly_users:
        user_table_data.append([
            f"{week['week_start']} - {week['week_end']}",
            str(week['new_users']),
            str(week['total_users']),
            f"{week['growth_percent']}%"
        ])
    
    user_table = Table(user_table_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(user_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Add the chart/graph
    if weekly_users:
        elements.append(Paragraph("<i>User Growth Chart:</i>", body_style))
        elements.append(create_user_growth_chart(weekly_users))
    elements.append(Spacer(1, 0.3*inch))
    
    # Meal Plans Generated - TABLE
    elements.append(Paragraph("<b>2.2 AI Meal Plans Generated (Weekly)</b>", body_style))
    weekly_meal_plans = context_data.get('weekly_meal_plans', [])
    meal_table_data = [['Week', 'Meal Plans Generated']]
    for week in weekly_meal_plans:
        meal_table_data.append([
            f"{week['week_start']} - {week['week_end']}",
            str(week['meal_plans'])
        ])
    
    meal_table = Table(meal_table_data, colWidths=[4*inch, 2.1*inch])
    meal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eef2ff')]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(meal_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Add the chart/graph
    if weekly_meal_plans:
        elements.append(Paragraph("<i>Meal Plans Chart:</i>", body_style))
        elements.append(create_bar_chart(weekly_meal_plans, 'Meal Plans', '#6366f1'))
    elements.append(Spacer(1, 0.3*inch))
    
    # Health Reports Generated - TABLE
    elements.append(Paragraph("<b>2.3 AI Health Reports Generated (Weekly)</b>", body_style))
    weekly_health_reports = context_data.get('weekly_health_reports', [])
    health_table_data = [['Week', 'Health Reports Generated']]
    for week in weekly_health_reports:
        health_table_data.append([
            f"{week['week_start']} - {week['week_end']}",
            str(week['health_reports'])
        ])
    
    health_table = Table(health_table_data, colWidths=[4*inch, 2.1*inch])
    health_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(health_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Add the chart/graph
    if weekly_health_reports:
        elements.append(Paragraph("<i>Health Reports Chart:</i>", body_style))
        elements.append(create_bar_chart(weekly_health_reports, 'Health Reports', '#ef4444'))
    elements.append(Spacer(1, 0.3*inch))
    
    # Returning Users
    elements.append(Paragraph("<b>2.4 Returning Users</b>", body_style))
    returning_data = [
        ['Period', 'Returning Users'],
        ['Last 7 Days', str(context_data.get('returning_users_7d', 0))],
        ['Last 30 Days', str(context_data.get('returning_users_30d', 0))]
    ]
    
    returning_table = Table(returning_data, colWidths=[4*inch, 2.1*inch])
    returning_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#faf5ff')]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(returning_table)
    
    # PAGE BREAK before next section
    elements.append(PageBreak())
    
    # ===== SECTION 3: SAMPLE MEAL PLAN =====
    elements.append(Paragraph("Section 3: Sample Meal Plan Output", header_style))
    
    sample_meal_plan = context_data.get('sample_meal_plan')
    sample_meal_plan_json = context_data.get('sample_meal_plan_json')
    sample_meal_plan_data = context_data.get('sample_meal_plan_data')
    
    if sample_meal_plan and sample_meal_plan_json:
        elements.append(Paragraph(
            f"<b>Sample Generated for Pet:</b> {sample_meal_plan.get('pet_name', 'N/A')}<br/>"
            f"<b>Generated on:</b> {sample_meal_plan.get('created_at', 'N/A')}<br/>"
            f"<b>Report Type:</b> AI-Powered Meal Plan",
            body_style
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add a note about UI and JSON outputs
        elements.append(Paragraph(
            "<b>Dual Output Format:</b> The platform generates both a beautiful user-facing interface "
            "and structured JSON data for API integration. This demonstrates our capability to serve "
            "both end-users and B2B clients.",
            body_style
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # ===== USER-FACING INTERFACE SCREENSHOT =====
        elements.append(Paragraph("<b>User-Facing Interface Output:</b>", header_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Try to load the meal plan UI screenshot
        meal_plan_image_path = os.path.join(settings.MEDIA_ROOT, 'evidence_screenshots', 'meal_plan_ui.png')
        if os.path.exists(meal_plan_image_path):
            try:
                img = Image(meal_plan_image_path, width=6.5*inch, height=4*inch, kind='proportional')
                elements.append(img)
            except Exception as e:
                elements.append(Paragraph(
                    f"<i>Screenshot not available. Please add meal_plan_ui.png to media/evidence_screenshots/</i>",
                    body_style
                ))
        else:
            elements.append(Paragraph(
                "<i>Screenshot placeholder: Add meal_plan_ui.png to media/evidence_screenshots/ folder to display the UI here.</i>",
                body_style
            ))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # JSON snippet (first 800 characters)
        elements.append(Paragraph("<b>JSON Output Sample (for API integration):</b>", body_style))
        json_preview = sample_meal_plan_json[:800] if len(sample_meal_plan_json) > 800 else sample_meal_plan_json
        if len(sample_meal_plan_json) > 800:
            json_preview += "\n... (truncated for brevity)"
        
        code_style = ParagraphStyle(
            'Code',
            parent=body_style,
            fontName='Courier',
            fontSize=6,
            leftIndent=20,
            textColor=colors.HexColor('#059669')
        )
        elements.append(Paragraph(f"<pre>{json_preview}</pre>", code_style))
    else:
        elements.append(Paragraph(
            "<i>No meal plan samples available at this time.</i>",
            body_style
        ))
    
    # PAGE BREAK before section 4
    elements.append(PageBreak())
    
    # ===== SECTION 4: SAMPLE HEALTH REPORT =====
    elements.append(Paragraph("Section 4: Sample Health Report Output", header_style))
    
    sample_health_report = context_data.get('sample_health_report')
    sample_health_report_json = context_data.get('sample_health_report_json')
    sample_health_report_data = context_data.get('sample_health_report_data')
    
    if sample_health_report and sample_health_report_json:
        elements.append(Paragraph(
            f"<b>Sample Generated for Pet:</b> {sample_health_report.get('pet_name', 'N/A')}<br/>"
            f"<b>Generated on:</b> {sample_health_report.get('created_at', 'N/A')}<br/>"
            f"<b>Report Type:</b> AI-Powered Health Assessment",
            body_style
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add a note about health reports
        elements.append(Paragraph(
            "<b>Dual Output Format:</b> Health reports provide breed-specific insights, health summaries, "
            "feeding tips, activity recommendations, and health monitoring alerts in both user-friendly "
            "and machine-readable formats.",
            body_style
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # ===== USER-FACING INTERFACE SCREENSHOT =====
        elements.append(Paragraph("<b>User-Facing Interface Output:</b>", header_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Try to load the health report UI screenshot
        health_report_image_path = os.path.join(settings.MEDIA_ROOT, 'evidence_screenshots', 'health_report_ui.png')
        if os.path.exists(health_report_image_path):
            try:
                img = Image(health_report_image_path, width=6.5*inch, height=4*inch, kind='proportional')
                elements.append(img)
            except Exception as e:
                elements.append(Paragraph(
                    f"<i>Screenshot not available. Please add health_report_ui.png to media/evidence_screenshots/</i>",
                    body_style
                ))
        else:
            elements.append(Paragraph(
                "<i>Screenshot placeholder: Add health_report_ui.png to media/evidence_screenshots/ folder to display the UI here.</i>",
                body_style
            ))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # JSON snippet (first 800 characters)
        elements.append(Paragraph("<b>JSON Output Sample (for API integration):</b>", body_style))
        json_preview = sample_health_report_json[:800] if len(sample_health_report_json) > 800 else sample_health_report_json
        if len(sample_health_report_json) > 800:
            json_preview += "\n... (truncated for brevity)"
        
        code_style = ParagraphStyle(
            'Code',
            parent=body_style,
            fontName='Courier',
            fontSize=6,
            leftIndent=20,
            textColor=colors.HexColor('#059669')
        )
        elements.append(Paragraph(f"<pre>{json_preview}</pre>", code_style))
    else:
        elements.append(Paragraph(
            "<i>No health report samples available at this time.</i>",
            body_style
        ))
    
    # PAGE BREAK before section 5
    elements.append(PageBreak())
    
    # ===== SECTION 5: PLATFORM DEMO =====
    elements.append(Paragraph("Section 5: Platform Demo Video", header_style))
    
    elements.append(Paragraph(
        "A comprehensive video demonstration of the FAMMO platform is available online, showcasing "
        "our AI-powered pet nutrition and health features in action.",
        body_style
    ))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph(
        "<b>Video URL:</b> <link href='https://youtu.be/39XQOxOkXww' color='blue'>https://youtu.be/39XQOxOkXww</link>",
        body_style
    ))
    elements.append(Spacer(1, 0.15*inch))
    
    # Demo highlights
    demo_data = [
        ['Feature', 'Description'],
        ['AI Meal Plans', 'Personalized nutrition recommendations based on pet profile'],
        ['Health Reports', 'Breed-specific health insights and monitoring alerts'],
        ['AI Chat', 'Interactive pet care assistance with contextual responses'],
        ['Multi-language', 'Support for English, Turkish, Finnish, and Dutch'],
    ]
    
    demo_table = Table(demo_data, colWidths=[2*inch, 4.1*inch])
    demo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f97316')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff7ed')]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(demo_table)
    
    # PAGE BREAK before next section
    elements.append(PageBreak())
    
    # ===== SECTION 6: AI TECHNOLOGY OVERVIEW =====
    elements.append(Paragraph("Section 6: Technology Overview – AI Nutrition Engine", header_style))
    
    tech_summary = """
    Our AI nutrition engine processes comprehensive pet profile data—including species, breed, age, weight, 
    body condition, allergies, health conditions, feeding history, and activity level—to deliver personalized 
    dietary recommendations. The system employs advanced feature engineering to convert raw inputs into structured 
    nutritional parameters such as caloric requirements (MER/DER), nutrient ratios, risk flags, and constraint sets. 
    Our AI model combines evidence-based veterinary nutrition guidelines with machine-learning rules to generate 
    tailored meal plans that respect breed-specific needs, age categories, allergy exclusions, and safe ingredient ranges. 
    All outputs are produced as deterministic JSON blocks containing meals, precise quantities, complete nutrition totals, 
    and critical safety notes, ensuring reproducibility and transparency. The engine enforces strict constraints around 
    calorie limits, macronutrient balance, and allergen avoidance to maintain pet health and safety. User behavior and 
    outcomes are continuously collected to refine the AI's recommendations over time, creating an adaptive feedback loop 
    that improves accuracy and personalization with each interaction.
    """
    
    elements.append(Paragraph(tech_summary, body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Core Technologies
    elements.append(Paragraph("<b>Core Technologies:</b>", body_style))
    tech_data = [
        ['Technology', 'Application'],
        ['AI/ML', 'Machine Learning for personalized recommendations'],
        ['JSON', 'Structured data format for API integration'],
        ['API', 'RESTful endpoints for third-party integration'],
        ['VET', 'Evidence-based veterinary nutrition guidelines']
    ]
    
    tech_table = Table(tech_data, colWidths=[2*inch, 4.1*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9333ea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#faf5ff')]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(tech_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = f"""
    <para alignment='center'>
    <i>This evidence summary was automatically generated on {current_date}</i><br/>
    <b>FAMMO - AI-Powered Pet Nutrition Platform</b><br/>
    For more information, visit <link href='https://fammo.ai' color='blue'>https://fammo.ai</link>
    </para>
    """
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    return response
