from modeltranslation.translator import register, TranslationOptions
from .models import HeroSection, FAQ, OnboardingSlide, LegalDocument

@register(HeroSection)
class HeroSectionTranslationOptions(TranslationOptions):
    fields = ('heading', 'subheading', 'subheading_secondary',)

@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer',)

@register(OnboardingSlide)
class OnboardingSlideTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'button_text',)

@register(LegalDocument)
class LegalDocumentTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'summary',)