"""
Automated screenshot generator for evidence dashboard UI sections.
Uses playwright to capture rendered HTML sections as PNG images.
"""
import os
import sys
from django.conf import settings
from pathlib import Path

# Ensure UTF-8 encoding for all string operations
if sys.platform != 'win32':  # Unix-like systems (including cPanel)
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        pass  # If locale not available, continue anyway


def generate_meal_plan_screenshot(html_content, output_path):
    """
    Generate screenshot of meal plan UI from HTML content.
    
    Args:
        html_content: HTML string of the meal plan UI
        output_path: Path where the screenshot should be saved
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Launch browser with additional args for restricted environments
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            page = browser.new_page(viewport={'width': 1200, 'height': 2400})
            
            # Ensure HTML content is properly encoded as UTF-8
            if isinstance(html_content, str):
                html_content = html_content.encode('utf-8').decode('utf-8')
            
            # Set the HTML content
            page.set_content(html_content, wait_until='networkidle')
            
            # Wait for any dynamic content to load
            page.wait_for_timeout(1500)
            
            # Take full-page screenshot
            page.screenshot(path=str(output_path), full_page=True)
            
            browser.close()
            return True
    except ImportError:
        print("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        return False
    except Exception as e:
        print(f"Error generating meal plan screenshot: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_health_report_screenshot(html_content, output_path):
    """
    Generate screenshot of health report UI from HTML content.
    
    Args:
        html_content: HTML string of the health report UI
        output_path: Path where the screenshot should be saved
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Launch browser with additional args for restricted environments
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            page = browser.new_page(viewport={'width': 1200, 'height': 2400})
            
            # Ensure HTML content is properly encoded as UTF-8
            if isinstance(html_content, str):
                html_content = html_content.encode('utf-8').decode('utf-8')
            
            # Set the HTML content
            page.set_content(html_content, wait_until='networkidle')
            
            # Wait for any dynamic content to load
            page.wait_for_timeout(1500)
            
            # Take full-page screenshot
            page.screenshot(path=str(output_path), full_page=True)
            
            browser.close()
            return True
    except ImportError:
        print("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        return False
    except Exception as e:
        print(f"Error generating health report screenshot: {e}")
        import traceback
        traceback.print_exc()
        return False


def ensure_screenshots_directory():
    """Ensure the evidence_screenshots directory exists."""
    screenshot_dir = os.path.join(settings.MEDIA_ROOT, 'evidence_screenshots')
    Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
    return screenshot_dir


def generate_section_screenshots_from_data(meal_plan_data, health_report_data):
    """
    Generate screenshots for both meal plan and health report sections.
    Creates standalone HTML and captures it as images.
    
    Args:
        meal_plan_data: Dictionary containing meal plan data
        health_report_data: Dictionary containing health report data
    
    Returns:
        tuple: (meal_plan_path, health_report_path) or (None, None) if failed
    """
    # Check if screenshot generation is enabled
    if not getattr(settings, 'ENABLE_PLAYWRIGHT_SCREENSHOTS', True):
        print("Screenshot generation disabled via ENABLE_PLAYWRIGHT_SCREENSHOTS setting")
        return None, None
    
    try:
        ensure_screenshots_directory()
        
        meal_plan_path = os.path.join(settings.MEDIA_ROOT, 'evidence_screenshots', 'meal_plan_ui.png')
        health_report_path = os.path.join(settings.MEDIA_ROOT, 'evidence_screenshots', 'health_report_ui.png')
        
        # Check if screenshots already exist and are recent (less than 1 hour old)
        # This avoids regenerating on every PDF download
        if os.path.exists(meal_plan_path) and os.path.exists(health_report_path):
            meal_plan_age = os.path.getmtime(meal_plan_path)
            health_report_age = os.path.getmtime(health_report_path)
            import time
            current_time = time.time()
            # If both files are less than 1 hour old, reuse them
            if (current_time - meal_plan_age < 3600) and (current_time - health_report_age < 3600):
                print("Using existing screenshots (less than 1 hour old)")
                return meal_plan_path, health_report_path
        
        # Generate meal plan HTML
        meal_plan_html = generate_meal_plan_html(meal_plan_data)
        if not generate_meal_plan_screenshot(meal_plan_html, meal_plan_path):
            meal_plan_path = None
        
        # Generate health report HTML
        health_report_html = generate_health_report_html(health_report_data)
        if not generate_health_report_screenshot(health_report_html, health_report_path):
            health_report_path = None
        
        return meal_plan_path, health_report_path
    except Exception as e:
        print(f"Screenshot generation failed: {e}")
        import traceback
        traceback.print_exc()
        # Return None for both paths if any error occurs
        return None, None


def generate_meal_plan_html(meal_plan_data):
    """Generate standalone HTML for meal plan UI - matches actual modal content."""
    if not meal_plan_data:
        return "<html><body><p>No meal plan data available</p></body></html>"
    
    der_kcal = meal_plan_data.get('der_kcal', 'N/A')
    nutrient_targets = meal_plan_data.get('nutrient_targets', {})
    protein = nutrient_targets.get('protein_percent', 'N/A')
    fat = nutrient_targets.get('fat_percent', 'N/A')
    carbs = nutrient_targets.get('carbs_percent', 'N/A')
    
    options = meal_plan_data.get('options', [])
    options_html = ""
    for idx, opt in enumerate(options, 1):
        sections_html = ""
        for sec in opt.get('sections', []):
            items_html = "".join([f'<li class="text-sm text-gray-700 flex items-start"><span class="mr-2 text-indigo-500">▸</span><span>{item}</span></li>' 
                                 for item in sec.get('items', [])])
            sections_html += f'''
            <div class="rounded-lg p-4 bg-gray-50 border border-gray-200">
                <h5 class="font-bold mb-2 text-indigo-600">{sec.get('title', '')}</h5>
                <ul class="space-y-1">{items_html}</ul>
            </div>
            '''
        
        options_html += f'''
        <div class="bg-white border-2 rounded-xl p-6 shadow-lg border-gray-200 mb-4">
            <div class="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-full inline-block font-bold text-sm mb-3">
                Option {idx}
            </div>
            <h4 class="text-xl font-bold mb-2">{opt.get('name', 'N/A')}</h4>
            <p class="text-gray-600 italic mb-4">{opt.get('overview', '')}</p>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sections_html}
            </div>
        </div>
        '''
    
    feeding_schedule = meal_plan_data.get('feeding_schedule', [])
    schedule_html = "".join([f'''
        <div class="bg-white rounded-lg p-4 border-l-4 border-green-500">
            <div class="font-bold text-green-700 mb-1">{sched.get('time', '')}</div>
            <div class="text-sm text-gray-700">{sched.get('note', '')}</div>
        </div>
    ''' for sched in feeding_schedule])
    
    safety_notes = meal_plan_data.get('safety_notes', [])
    safety_html = "".join([f'''
        <div class="bg-white rounded-lg p-4 border-l-4 border-red-500">
            <div class="text-sm text-gray-700 flex items-start">
                <span class="text-red-600 mr-2 font-bold">•</span>
                <span>{note}</span>
            </div>
        </div>
    ''' for note in safety_notes])
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                margin: 0;
                padding: 0;
                background: white;
            }}
            .modal-header {{
                background: linear-gradient(to right, rgb(79, 70, 229), rgb(147, 51, 234), rgb(219, 39, 119));
                padding: 16px 32px;
                display: flex;
                align-items: center;
            }}
            .modal-header h3 {{
                color: white;
                font-size: 20px;
                font-weight: bold;
                margin: 0;
            }}
            .modal-content {{
                padding: 32px;
            }}
            .grid-2 {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 24px;
                margin-bottom: 24px;
            }}
            .card {{
                border: 2px solid;
                border-radius: 12px;
                padding: 24px;
            }}
            .card-yellow {{
                background: linear-gradient(to bottom right, rgb(254, 243, 199), rgb(253, 230, 138));
                border-color: rgb(254, 240, 138);
            }}
            .card-blue {{
                background: linear-gradient(to bottom right, rgb(219, 234, 254), rgb(191, 219, 254));
                border-color: rgb(147, 197, 253);
            }}
            .energy-value {{
                font-size: 48px;
                font-weight: 800;
                color: rgb(234, 88, 12);
                margin: 16px 0;
            }}
            .nutrient-row {{
                display: flex;
                justify-content: space-between;
                background: white;
                border-radius: 8px;
                padding: 8px 12px;
                margin-bottom: 8px;
            }}
            .nutrient-label {{ font-weight: 500; }}
            .nutrient-value {{ font-weight: 700; color: rgb(37, 99, 235); }}
            .section-title {{
                font-size: 24px;
                font-weight: 700;
                margin: 24px 0 16px 0;
                display: flex;
                align-items: center;
            }}
            .option-badge {{
                background: linear-gradient(to right, rgb(147, 51, 234), rgb(219, 39, 119));
                color: white;
                padding: 8px 16px;
                border-radius: 9999px;
                font-weight: 700;
                font-size: 14px;
                display: inline-block;
                margin-bottom: 12px;
            }}
            .option-box {{
                background: white;
                border: 2px solid rgb(229, 231, 235);
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 16px;
            }}
            .option-title {{ font-size: 20px; font-weight: 700; margin-bottom: 8px; }}
            .option-desc {{ color: rgb(107, 114, 128); font-style: italic; margin-bottom: 16px; }}
            .grid-3 {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
            }}
            .meal-section {{
                background: rgb(249, 250, 251);
                border: 1px solid rgb(229, 231, 235);
                border-radius: 8px;
                padding: 16px;
            }}
            .meal-section h5 {{
                font-weight: 700;
                color: rgb(99, 102, 241);
                margin: 0 0 8px 0;
            }}
            .meal-section ul {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            .meal-section li {{
                font-size: 14px;
                color: rgb(55, 65, 81);
                display: flex;
                align-items: start;
                margin-bottom: 4px;
            }}
            .schedule-box {{
                border: 2px solid rgb(134, 239, 172);
                background: linear-gradient(to bottom right, rgb(220, 252, 231), rgb(167, 243, 208));
                border-radius: 12px;
                padding: 24px;
            }}
            .safety-box {{
                border: 2px solid rgb(254, 202, 202);
                background: linear-gradient(to bottom right, rgb(254, 242, 242), rgb(254, 215, 170));
                border-radius: 12px;
                padding: 24px;
            }}
            .schedule-item, .safety-item {{
                background: white;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 12px;
            }}
            .schedule-item {{
                border-left: 4px solid rgb(34, 197, 94);
            }}
            .safety-item {{
                border-left: 4px solid rgb(239, 68, 68);
            }}
            h3.box-title {{
                font-size: 18px;
                font-weight: 700;
                margin: 0 0 16px 0;
                display: flex;
                align-items: center;
            }}
        </style>
    </head>
    <body>
        <div class="modal-header">
            <h3>📱 Full Meal Plan UI Preview</h3>
        </div>
        <div class="modal-content">
            <!-- DER & Nutrients -->
            <div class="grid-2">
                <div class="card card-yellow">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 32px; margin-right: 12px;">⚡</span>
                        <h3 style="font-weight: 700; font-size: 18px; color: rgb(120, 53, 15); margin: 0;">Daily Energy Requirement</h3>
                    </div>
                    <p class="energy-value">{der_kcal}</p>
                    <p style="font-weight: 500; color: rgb(194, 65, 12); margin: 8px 0 0 0;">Target Kilocalories (kcal)</p>
                </div>
                <div class="card card-blue">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 32px; margin-right: 12px;">📊</span>
                        <h3 style="font-weight: 700; font-size: 18px; color: rgb(30, 58, 138); margin: 0;">Nutrient Breakdown</h3>
                    </div>
                    <div style="margin-top: 16px;">
                        <div class="nutrient-row">
                            <span class="nutrient-label">🥩 Protein:</span>
                            <span class="nutrient-value">{protein}</span>
                        </div>
                        <div class="nutrient-row">
                            <span class="nutrient-label">🥑 Fat:</span>
                            <span class="nutrient-value">{fat}</span>
                        </div>
                        <div class="nutrient-row">
                            <span class="nutrient-label">🌾 Carbs:</span>
                            <span class="nutrient-value">{carbs}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Meal Options -->
            <h3 class="section-title">
                <span style="font-size: 32px; margin-right: 12px;">🍴</span>
                Meal Plan Options
            </h3>
            {options_html}
            
            <!-- Feeding Schedule & Safety -->
            <div class="grid-2" style="margin-top: 24px;">
                <div class="schedule-box">
                    <h3 class="box-title">
                        <span style="font-size: 24px; margin-right: 8px;">🕐</span>
                        <span style="color: rgb(20, 83, 45);">Recommended Feeding Schedule</span>
                    </h3>
                    {schedule_html}
                </div>
                <div class="safety-box">
                    <h3 class="box-title">
                        <span style="font-size: 24px; margin-right: 8px;">⚠️</span>
                        <span style="color: rgb(127, 29, 29);">Crucial Safety & Transition Notes</span>
                    </h3>
                    {safety_html}
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    return html


def generate_health_report_html(health_report_data):
    """Generate standalone HTML for health report UI - matches actual modal content."""
    if not health_report_data:
        return "<html><body><p>No health report data available</p></body></html>"
    
    health_summary = health_report_data.get('health_summary', '')
    activity = health_report_data.get('activity', '')
    weight_diet = health_report_data.get('weight_and_diet', '')
    
    feeding_tips = health_report_data.get('feeding_tips', [])
    tips_html = "".join([f'''
        <li style="display: flex; align-items: start; margin-bottom: 8px;">
            <i style="color: rgb(202, 138, 4); margin-right: 8px; margin-top: 4px;">✓</i>
            <span style="color: rgb(55, 65, 81);">{tip}</span>
        </li>
    ''' for tip in feeding_tips])
    
    breed_risks = health_report_data.get('breed_risks', [])
    risks_html = "".join([f'''
        <li style="display: flex; align-items: start; background: white; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
            <i style="color: rgb(220, 38, 38); margin-right: 8px; margin-top: 4px;">⚠</i>
            <span style="color: rgb(55, 65, 81);">{risk}</span>
        </li>
    ''' for risk in breed_risks])
    
    alerts = health_report_data.get('alerts', [])
    alerts_html = "".join([f'''
        <li style="display: flex; align-items: start; background: white; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
            <i style="color: rgb(22, 163, 74); margin-right: 8px; margin-top: 4px;">👁</i>
            <span style="color: rgb(55, 65, 81);">{alert}</span>
        </li>
    ''' for alert in alerts])
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                margin: 0;
                padding: 0;
                background: white;
            }}
            .modal-header {{
                background: linear-gradient(to right, rgb(220, 38, 38), rgb(249, 115, 22), rgb(219, 39, 119));
                padding: 16px 32px;
                display: flex;
                align-items: center;
            }}
            .modal-header h3 {{
                color: white;
                font-size: 20px;
                font-weight: bold;
                margin: 0;
            }}
            .modal-content {{
                padding: 32px;
            }}
            .section {{
                border: 2px solid;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 24px;
            }}
            .section-header {{
                background: linear-gradient(to right, rgb(254, 242, 242), rgb(254, 215, 170));
                border: 2px solid rgb(254, 202, 202);
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 24px;
            }}
            .section-header h2 {{
                font-size: 30px;
                font-weight: 700;
                color: rgb(127, 29, 29);
                margin: 0 0 8px 0;
            }}
            .section-header p {{
                color: rgb(75, 85, 99);
                margin: 0;
            }}
            .blue-section {{
                background: rgb(239, 246, 255);
                border-color: rgb(147, 197, 253);
            }}
            .orange-section {{
                background: rgb(255, 237, 213);
                border-color: rgb(251, 191, 36);
            }}
            .purple-section {{
                background: rgb(250, 245, 255);
                border-color: rgb(216, 180, 254);
            }}
            .yellow-section {{
                background: rgb(254, 249, 195);
                border-color: rgb(250, 204, 21);
            }}
            .red-section {{
                background: rgb(254, 242, 242);
                border-color: rgb(252, 165, 165);
            }}
            .green-section {{
                background: rgb(240, 253, 244);
                border-color: rgb(134, 239, 172);
            }}
            .section-title {{
                font-size: 20px;
                font-weight: 700;
                margin: 0 0 12px 0;
                display: flex;
                align-items: center;
            }}
            .section-title i {{
                margin-right: 8px;
            }}
            .blue-title {{ color: rgb(30, 58, 138); }}
            .orange-title {{ color: rgb(124, 45, 18); }}
            .purple-title {{ color: rgb(88, 28, 135); }}
            .yellow-title {{ color: rgb(113, 63, 18); }}
            .red-title {{ color: rgb(127, 29, 29); }}
            .green-title {{ color: rgb(20, 83, 45); }}
            .section-text {{
                color: rgb(55, 65, 81);
                line-height: 1.6;
            }}
            .grid-2 {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 24px;
                margin-bottom: 24px;
            }}
            ul {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            .risks-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="modal-header">
            <h3>🏥 Full Health Report UI Preview</h3>
        </div>
        <div class="modal-content">
            <!-- Header -->
            <div class="section-header">
                <h2>
                    <i style="margin-right: 8px;">❤️</i>
                    AI Health Assessment
                </h2>
                <p>Comprehensive health analysis with breed-specific insights</p>
            </div>

            <!-- Health Summary -->
            <div class="section blue-section">
                <h3 class="section-title blue-title">
                    <i>📋</i>Health Summary
                </h3>
                <p class="section-text">{health_summary}</p>
            </div>

            <!-- Activity & Weight/Diet -->
            <div class="grid-2">
                <div class="section orange-section">
                    <h3 class="section-title orange-title">
                        <i>🏃</i>Activity Recommendations
                    </h3>
                    <p class="section-text">{activity}</p>
                </div>
                <div class="section purple-section">
                    <h3 class="section-title purple-title">
                        <i>⚖️</i>Weight & Diet Analysis
                    </h3>
                    <p class="section-text">{weight_diet}</p>
                </div>
            </div>

            <!-- Feeding Tips -->
            <div class="section yellow-section">
                <h3 class="section-title yellow-title">
                    <i>🍽️</i>Feeding Tips
                </h3>
                <ul>
                    {tips_html}
                </ul>
            </div>

            <!-- Breed Risks -->
            <div class="section red-section">
                <h3 class="section-title red-title">
                    <i>⚠️</i>Breed-Specific Health Risks
                </h3>
                <ul class="risks-grid">
                    {risks_html}
                </ul>
            </div>

            <!-- Health Alerts -->
            <div class="section green-section">
                <h3 class="section-title green-title">
                    <i>🔔</i>Health Monitoring Alerts
                </h3>
                <ul>
                    {alerts_html}
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''
    return html
