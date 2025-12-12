"""
Management command to seed legal documents for FAMMO platform.

This creates the initial legal documents in English, which can then be translated
through the Django admin interface using django-modeltranslation.

Usage:
    python manage.py seed_legal_documents
    python manage.py seed_legal_documents --update  # Update existing documents
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.models import LegalDocument, DocumentType


class Command(BaseCommand):
    help = 'Seeds legal documents (Terms, Privacy, Agreements) for FAMMO platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing documents instead of creating new ones',
        )

    def handle(self, *args, **options):
        update_mode = options['update']
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Seeding Legal Documents for FAMMO Platform'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        documents = [
            {
                'doc_type': DocumentType.USER_TERMS_CONDITIONS,
                'title': 'FAMMO User Terms and Conditions',
                'version': '1.0',
                'summary': 'Terms and Conditions for FAMMO platform users.',
                'content': self.get_user_terms_content(),
            },
            {
                'doc_type': DocumentType.USER_PRIVACY_POLICY,
                'title': 'FAMMO Privacy Policy',
                'version': '1.0',
                'summary': 'Privacy Policy for FAMMO platform users.',
                'content': self.get_user_privacy_content(),
            },
            {
                'doc_type': DocumentType.CLINIC_TERMS_CONDITIONS,
                'title': 'FAMMO Clinic Terms and Conditions',
                'version': '1.0',
                'summary': 'Terms and Conditions for veterinary clinics partnering with FAMMO.',
                'content': self.get_clinic_terms_content(),
            },
            {
                'doc_type': DocumentType.CLINIC_PARTNERSHIP,
                'title': 'FAMMO Clinic Partnership Agreement',
                'version': '1.0',
                'summary': 'Partnership Agreement between FAMMO and veterinary clinics.',
                'content': self.get_clinic_partnership_content(),
            },
            {
                'doc_type': DocumentType.CLINIC_EOI,
                'title': 'Expression of Interest (EOI) Terms',
                'version': '1.0',
                'summary': 'Terms for clinics expressing interest in FAMMO pilot program.',
                'content': self.get_eoi_terms_content(),
            },
        ]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for doc_data in documents:
            doc_type = doc_data['doc_type']
            
            try:
                # Try to get existing active document
                existing = LegalDocument.objects.filter(
                    doc_type=doc_type,
                    is_active=True
                ).first()
                
                if existing and not update_mode:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⏭️  Skipped: {doc_data["title"]} (already exists, use --update to modify)'
                        )
                    )
                    skipped_count += 1
                    continue
                
                if existing and update_mode:
                    # Update existing document
                    existing.title = doc_data['title']
                    existing.version = doc_data['version']
                    existing.summary = doc_data['summary']
                    existing.content = doc_data['content']
                    existing.effective_date = timezone.now()
                    existing.admin_notes = 'Updated via seed_legal_documents command'
                    existing.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Updated: {doc_data["title"]} (v{doc_data["version"]})'
                        )
                    )
                    updated_count += 1
                else:
                    # Create new document
                    LegalDocument.objects.create(
                        doc_type=doc_type,
                        title=doc_data['title'],
                        version=doc_data['version'],
                        summary=doc_data['summary'],
                        content=doc_data['content'],
                        is_active=True,
                        effective_date=timezone.now(),
                        admin_notes='Created via seed_legal_documents command'
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Created: {doc_data["title"]} (v{doc_data["version"]})'
                        )
                    )
                    created_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error processing {doc_data["title"]}: {str(e)}'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('Summary:'))
        self.stdout.write(self.style.SUCCESS(f'  Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Updated: {updated_count}'))
        self.stdout.write(self.style.WARNING(f'  Skipped: {skipped_count}'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        if created_count > 0 or updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✨ Legal documents seeded successfully!'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '\n💡 Note: You can now translate these documents to other languages'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '   via the Django admin panel (modeltranslation fields).'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    '\nℹ️  No documents were created or updated.'
                )
            )

    def get_user_terms_content(self):
        """User Terms and Conditions content"""
        return """
<h1>FAMMO User Terms and Conditions</h1>
<p><strong>Last Updated:</strong> January 2025</p>

<h2>1. Introduction</h2>
<p>Welcome to FAMMO! These Terms and Conditions ("Terms") govern your use of the FAMMO platform, 
including our website and mobile applications (collectively, the "Platform"). By accessing or using 
the Platform, you agree to be bound by these Terms.</p>

<h2>2. Use of the Platform</h2>
<p>FAMMO provides AI-powered pet nutrition recommendations and health insights. You agree to:</p>
<ul>
    <li>Provide accurate information about your pet</li>
    <li>Use the Platform for lawful purposes only</li>
    <li>Not misuse or attempt to compromise the Platform's security</li>
    <li>Respect the intellectual property rights of FAMMO and others</li>
</ul>

<h2>3. Pet Information and Recommendations</h2>
<p>The recommendations provided by FAMMO are based on AI analysis and should not replace 
professional veterinary advice. Always consult with a qualified veterinarian for medical concerns.</p>

<h2>4. User Accounts</h2>
<p>You are responsible for maintaining the confidentiality of your account credentials and for all 
activities that occur under your account.</p>

<h2>5. Data Privacy</h2>
<p>Your privacy is important to us. Please review our Privacy Policy to understand how we collect, 
use, and protect your personal information.</p>

<h2>6. Intellectual Property</h2>
<p>All content on the Platform, including text, graphics, logos, and software, is the property of 
FAMMO or its licensors and is protected by copyright and intellectual property laws.</p>

<h2>7. Limitation of Liability</h2>
<p>FAMMO is provided "as is" without warranties of any kind. We are not liable for any damages 
arising from your use of the Platform.</p>

<h2>8. Changes to Terms</h2>
<p>We may update these Terms from time to time. We will notify you of significant changes by posting 
the new Terms on the Platform.</p>

<h2>9. Contact Us</h2>
<p>If you have questions about these Terms, please contact us at <a href="mailto:legal@fammo.ai">legal@fammo.ai</a></p>
"""

    def get_user_privacy_content(self):
        """User Privacy Policy content"""
        return """
<h1>FAMMO Privacy Policy</h1>
<p><strong>Last Updated:</strong> January 2025</p>

<h2>1. Introduction</h2>
<p>FAMMO ("we," "us," or "our") respects your privacy and is committed to protecting your personal data. 
This Privacy Policy explains how we collect, use, and safeguard your information.</p>

<h2>2. Information We Collect</h2>
<h3>2.1 Information You Provide</h3>
<ul>
    <li>Account information (email, name)</li>
    <li>Pet information (name, breed, age, weight, health conditions)</li>
    <li>Communication preferences</li>
</ul>

<h3>2.2 Automatically Collected Information</h3>
<ul>
    <li>Device information and IP address</li>
    <li>Usage data and analytics</li>
    <li>Location data (with your permission)</li>
</ul>

<h2>3. How We Use Your Information</h2>
<p>We use your information to:</p>
<ul>
    <li>Provide personalized pet nutrition recommendations</li>
    <li>Improve our AI algorithms and services</li>
    <li>Send you updates and notifications</li>
    <li>Comply with legal obligations</li>
</ul>

<h2>4. Data Sharing</h2>
<p>We do not sell your personal data. We may share your information with:</p>
<ul>
    <li>Partner veterinary clinics (with your consent)</li>
    <li>Service providers who help us operate the Platform</li>
    <li>Legal authorities when required by law</li>
</ul>

<h2>5. Data Security</h2>
<p>We implement appropriate technical and organizational measures to protect your personal data against 
unauthorized access, alteration, or destruction.</p>

<h2>6. Your Rights</h2>
<p>You have the right to:</p>
<ul>
    <li>Access your personal data</li>
    <li>Correct inaccurate information</li>
    <li>Request deletion of your data</li>
    <li>Object to data processing</li>
    <li>Data portability</li>
</ul>

<h2>7. Cookies and Tracking</h2>
<p>We use cookies and similar technologies to improve your experience on the Platform. You can manage 
cookie preferences through your browser settings.</p>

<h2>8. Children's Privacy</h2>
<p>Our Platform is not intended for users under 18 years of age. We do not knowingly collect data from children.</p>

<h2>9. Changes to This Policy</h2>
<p>We may update this Privacy Policy periodically. We will notify you of significant changes.</p>

<h2>10. Contact Us</h2>
<p>For privacy-related questions, contact us at <a href="mailto:privacy@fammo.ai">privacy@fammo.ai</a></p>
"""

    def get_clinic_terms_content(self):
        """Clinic Terms and Conditions content"""
        return """
<h1>FAMMO Clinic Terms and Conditions</h1>
<p><strong>Last Updated:</strong> January 2025</p>

<h2>1. Introduction</h2>
<p>These Terms and Conditions ("Terms") govern the relationship between FAMMO and veterinary clinics 
("Clinics") that partner with our platform.</p>

<h2>2. Clinic Registration</h2>
<p>By registering your clinic on FAMMO, you represent that:</p>
<ul>
    <li>You are authorized to act on behalf of the clinic</li>
    <li>All information provided is accurate and current</li>
    <li>Your clinic is properly licensed and insured</li>
    <li>You have the necessary qualifications and credentials</li>
</ul>

<h2>3. Clinic Profile and Information</h2>
<p>You agree to:</p>
<ul>
    <li>Maintain accurate clinic information on the Platform</li>
    <li>Update your profile regularly with current services and hours</li>
    <li>Respond promptly to user inquiries and referrals</li>
    <li>Provide professional and ethical veterinary services</li>
</ul>

<h2>4. Referrals and Patient Care</h2>
<p>FAMMO may refer users to your clinic based on location and services. You agree to:</p>
<ul>
    <li>Treat all referred patients professionally and ethically</li>
    <li>Maintain appropriate veterinary standards of care</li>
    <li>Respect patient privacy and confidentiality</li>
    <li>Comply with all applicable veterinary regulations</li>
</ul>

<h2>5. Data and Privacy</h2>
<p>You agree to protect user data and comply with applicable data protection laws. User data should 
only be used for providing veterinary services.</p>

<h2>6. Fees and Payment</h2>
<p>FAMMO's partnership model and any associated fees will be communicated separately. Currently, 
clinic registration is free during our pilot program.</p>

<h2>7. Intellectual Property</h2>
<p>You grant FAMMO a license to use your clinic name, logo, and information for marketing and 
promotional purposes on the Platform.</p>

<h2>8. Liability and Indemnification</h2>
<p>You agree to indemnify FAMMO against claims arising from your veterinary services or breach of 
these Terms.</p>

<h2>9. Termination</h2>
<p>Either party may terminate this agreement with written notice. FAMMO reserves the right to 
suspend or remove clinics that violate these Terms.</p>

<h2>10. Contact</h2>
<p>For questions about these Terms, contact us at <a href="mailto:clinics@fammo.ai">clinics@fammo.ai</a></p>
"""

    def get_clinic_partnership_content(self):
        """Clinic Partnership Agreement content"""
        return """
<h1>FAMMO Clinic Partnership Agreement</h1>
<p><strong>Last Updated:</strong> January 2025</p>

<h2>1. Partnership Overview</h2>
<p>This Partnership Agreement ("Agreement") establishes a collaborative relationship between FAMMO 
and your veterinary clinic to provide enhanced pet care services to our users.</p>

<h2>2. Partnership Benefits</h2>
<p>As a FAMMO partner clinic, you will receive:</p>
<ul>
    <li>Featured placement in our clinic directory</li>
    <li>Direct referrals from FAMMO users in your area</li>
    <li>Access to AI-generated pet health insights</li>
    <li>Marketing support and promotional opportunities</li>
    <li>Analytics and referral tracking tools</li>
</ul>

<h2>3. Partner Responsibilities</h2>
<p>As a partner clinic, you agree to:</p>
<ul>
    <li>Provide high-quality veterinary care to referred patients</li>
    <li>Maintain current clinic information on the Platform</li>
    <li>Respond to inquiries within 24-48 hours</li>
    <li>Participate in feedback and quality improvement initiatives</li>
    <li>Use FAMMO marketing materials appropriately</li>
</ul>

<h2>4. Referral Process</h2>
<p>FAMMO will refer users to partner clinics based on:</p>
<ul>
    <li>Geographic proximity to the user</li>
    <li>Clinic specializations and services</li>
    <li>User preferences and pet needs</li>
    <li>Clinic availability and capacity</li>
</ul>

<h2>5. Data Sharing and Privacy</h2>
<p>Both parties agree to:</p>
<ul>
    <li>Comply with applicable data protection regulations</li>
    <li>Use shared data only for agreed purposes</li>
    <li>Implement appropriate security measures</li>
    <li>Notify each other of any data breaches</li>
</ul>

<h2>6. Financial Terms</h2>
<p>During the pilot phase:</p>
<ul>
    <li>No partnership fees or commissions apply</li>
    <li>Clinics set their own pricing for services</li>
    <li>FAMMO does not process payments for veterinary services</li>
</ul>
<p>Future partnership models may include shared revenue or subscription options, to be communicated 
separately.</p>

<h2>7. Branding and Marketing</h2>
<p>Partner clinics may:</p>
<ul>
    <li>Display FAMMO partner badges and certificates</li>
    <li>Reference the partnership in marketing materials</li>
    <li>Participate in joint promotional campaigns</li>
</ul>
<p>All marketing materials must comply with FAMMO brand guidelines.</p>

<h2>8. Quality Standards</h2>
<p>Partner clinics must:</p>
<ul>
    <li>Maintain valid veterinary licenses</li>
    <li>Carry appropriate professional liability insurance</li>
    <li>Follow ethical veterinary practices</li>
    <li>Maintain clinic facilities to professional standards</li>
</ul>

<h2>9. Term and Termination</h2>
<p>This Agreement is effective from the date of acceptance and continues until terminated by either 
party with 30 days written notice.</p>

<h2>10. Dispute Resolution</h2>
<p>Any disputes will be resolved through good-faith negotiation, followed by mediation if necessary.</p>

<h2>11. Contact</h2>
<p>For partnership inquiries, contact <a href="mailto:partnerships@fammo.ai">partnerships@fammo.ai</a></p>
"""

    def get_eoi_terms_content(self):
        """Expression of Interest (EOI) Terms content"""
        return """
<h1>Expression of Interest (EOI) Terms</h1>
<p><strong>Last Updated:</strong> January 2025</p>

<h2>1. About the EOI Program</h2>
<p>The FAMMO Expression of Interest (EOI) program allows veterinary clinics to express interest in 
participating in our pilot program and future collaboration opportunities.</p>

<h2>2. What EOI Means</h2>
<p>By submitting an Expression of Interest, you indicate that:</p>
<ul>
    <li>Your clinic is interested in learning more about FAMMO</li>
    <li>You wish to be considered for pilot program participation</li>
    <li>You consent to receiving updates about FAMMO's clinic partnership program</li>
    <li>You may be interested in future collaboration opportunities</li>
</ul>

<h2>3. Non-Binding Nature</h2>
<p>Submitting an EOI is <strong>not binding</strong>. It does not:</p>
<ul>
    <li>Create any contractual obligations</li>
    <li>Guarantee acceptance into the pilot program</li>
    <li>Require any financial commitment</li>
    <li>Obligate you to use FAMMO services</li>
</ul>

<h2>4. Selection Process</h2>
<p>FAMMO will review EOI submissions based on:</p>
<ul>
    <li>Geographic distribution and coverage needs</li>
    <li>Clinic specializations and service offerings</li>
    <li>Capacity to participate in pilot programs</li>
    <li>Strategic partnership opportunities</li>
</ul>

<h2>5. Communication and Updates</h2>
<p>By submitting an EOI, you consent to:</p>
<ul>
    <li>Receive email updates about FAMMO's clinic program</li>
    <li>Be contacted about pilot program opportunities</li>
    <li>Receive surveys and feedback requests</li>
    <li>Invitations to webinars and information sessions</li>
</ul>

<h2>6. Data Usage</h2>
<p>Information provided in your EOI will be used to:</p>
<ul>
    <li>Evaluate your clinic for program participation</li>
    <li>Send relevant program updates and opportunities</li>
    <li>Understand market demand and geographic coverage</li>
    <li>Plan future partnership initiatives</li>
</ul>

<h2>7. Opt-Out</h2>
<p>You may withdraw your EOI or opt-out of communications at any time by:</p>
<ul>
    <li>Clicking "unsubscribe" in any email</li>
    <li>Contacting us at <a href="mailto:eoi@fammo.ai">eoi@fammo.ai</a></li>
    <li>Updating your communication preferences in your clinic profile</li>
</ul>

<h2>8. Privacy</h2>
<p>Your EOI information will be handled in accordance with FAMMO's Privacy Policy and applicable 
data protection laws.</p>

<h2>9. No Guarantee of Acceptance</h2>
<p>Submitting an EOI does not guarantee:</p>
<ul>
    <li>Selection for the pilot program</li>
    <li>Future partnership opportunities</li>
    <li>Any specific timeline for program launch</li>
</ul>

<h2>10. Next Steps</h2>
<p>After submitting your EOI:</p>
<ul>
    <li>You'll receive a confirmation email</li>
    <li>We'll review your submission</li>
    <li>Selected clinics will be contacted with more information</li>
    <li>All EOI participants will receive program updates</li>
</ul>

<h2>11. Questions</h2>
<p>For EOI-related questions, contact <a href="mailto:eoi@fammo.ai">eoi@fammo.ai</a></p>
"""
