"""
Management command to seed AppointmentReason data with translations.

Usage:
    python manage.py seed_appointment_reasons
    python manage.py seed_appointment_reasons --clear  # Clear existing before seeding

This will populate the AppointmentReason table with common veterinary visit reasons
in multiple languages (EN, TR, NL, FI) - sorted alphabetically by English name.
"""

from django.core.management.base import BaseCommand
from vets.models import AppointmentReason


# Appointment reasons data - sorted alphabetically by English name
APPOINTMENT_REASONS = [
    {
        "name_en": "Annual Wellness Exam",
        "description_en": "Routine yearly checkup",
        "name_tr": "Yıllık Sağlık Kontrolü",
        "description_tr": "Rutin yıllık muayene",
        "name_nl": "Jaarlijkse Gezondheidscontrole",
        "description_nl": "Jaarlijkse routinecontrole",
        "name_fi": "Vuosittainen terveystarkastus",
        "description_fi": "Rutiininomainen vuosikontrolli",
    },
    {
        "name_en": "Behavior Consultation",
        "description_en": "Anxiety or aggression issues",
        "name_tr": "Davranış Danışmanlığı",
        "description_tr": "Kaygı veya agresyon sorunları",
        "name_nl": "Gedragsconsult",
        "description_nl": "Angst- of agressieproblemen",
        "name_fi": "Käytösneuvonta",
        "description_fi": "Ahdistus- tai aggressio-ongelmat",
    },
    {
        "name_en": "Dental Checkup",
        "description_en": "Oral health examination",
        "name_tr": "Diş Kontrolü",
        "description_tr": "Ağız ve diş sağlığı muayenesi",
        "name_nl": "Gebitscontrole",
        "description_nl": "Mondgezondheidsonderzoek",
        "name_fi": "Hammastarkastus",
        "description_fi": "Suun ja hampaiden tarkastus",
    },
    {
        "name_en": "Dental Cleaning",
        "description_en": "Professional teeth cleaning",
        "name_tr": "Diş Temizliği",
        "description_tr": "Profesyonel diş temizliği",
        "name_nl": "Gebitsreiniging",
        "description_nl": "Professionele reiniging van tanden",
        "name_fi": "Hammaskiven poisto",
        "description_fi": "Ammattimainen hampaiden puhdistus",
    },
    {
        "name_en": "Deworming",
        "description_en": "Internal parasite treatment",
        "name_tr": "İç Parazit Tedavisi",
        "description_tr": "İç parazitlere karşı tedavi",
        "name_nl": "Ontworming",
        "description_nl": "Behandeling tegen inwendige parasieten",
        "name_fi": "Sisäloishäätö",
        "description_fi": "Sisäloisten hoito",
    },
    {
        "name_en": "Digestive Issues",
        "description_en": "Vomiting, diarrhea, or loss of appetite",
        "name_tr": "Sindirim Problemleri",
        "description_tr": "Kusma, ishal veya iştahsızlık",
        "name_nl": "Spijsverteringsproblemen",
        "description_nl": "Braken, diarree of verminderde eetlust",
        "name_fi": "Ruoansulatusongelmat",
        "description_fi": "Oksentelu, ripuli tai ruokahaluttomuus",
    },
    {
        "name_en": "Ear Infection",
        "description_en": "Scratching, odor, or head shaking",
        "name_tr": "Kulak Enfeksiyonu",
        "description_tr": "Kaşıma, koku veya baş sallama",
        "name_nl": "Oorontsteking",
        "description_nl": "Krabben, geur of hoofdschudden",
        "name_fi": "Korvatulehdus",
        "description_fi": "Raapiminen, haju tai pään ravistelu",
    },
    {
        "name_en": "Emergency / Urgent Care",
        "description_en": "Acute illness or injury",
        "name_tr": "Acil Müdahale",
        "description_tr": "Ani hastalık veya yaralanma",
        "name_nl": "Spoedzorg",
        "description_nl": "Acute ziekte of letsel",
        "name_fi": "Päivystyshoito",
        "description_fi": "Äkillinen sairaus tai vamma",
    },
    {
        "name_en": "Eye Problems",
        "description_en": "Discharge, redness, or cloudiness",
        "name_tr": "Göz Problemleri",
        "description_tr": "Akıntı, kızarıklık veya bulanıklık",
        "name_nl": "Oogproblemen",
        "description_nl": "Afscheiding, roodheid of troebelheid",
        "name_fi": "Silmäongelmat",
        "description_fi": "Vuoto, punoitus tai samentuma",
    },
    {
        "name_en": "Flea & Tick Prevention",
        "description_en": "Preventive treatment consultation",
        "name_tr": "Pire ve Kene Koruması",
        "description_tr": "Önleyici tedavi danışmanlığı",
        "name_nl": "Vlo- en Tekenpreventie",
        "description_nl": "Preventieve behandeling en advies",
        "name_fi": "Kirppu- ja Punkkitorjunta",
        "description_fi": "Ennaltaehkäisevä hoito ja neuvonta",
    },
    {
        "name_en": "Follow-up Visit",
        "description_en": "Post-treatment checkup",
        "name_tr": "Kontrol Ziyareti",
        "description_tr": "Tedavi sonrası kontrol",
        "name_nl": "Controlebezoek",
        "description_nl": "Nazorgcontrole",
        "name_fi": "Seurantakäynti",
        "description_fi": "Hoidon jälkeinen tarkastus",
    },
    {
        "name_en": "Grooming Services",
        "description_en": "Professional grooming if offered",
        "name_tr": "Tımar Hizmetleri",
        "description_tr": "Profesyonel bakım hizmeti",
        "name_nl": "Verzorging",
        "description_nl": "Professionele verzorging",
        "name_fi": "Turkinhoito",
        "description_fi": "Ammattimainen hoito",
    },
    {
        "name_en": "Health Certificate",
        "description_en": "Official travel documentation",
        "name_tr": "Sağlık Sertifikası",
        "description_tr": "Resmi seyahat belgesi",
        "name_nl": "Gezondheidsverklaring",
        "description_nl": "Officiële reisdocumentatie",
        "name_fi": "Terveystodistus",
        "description_fi": "Virallinen matkustusasiakirja",
    },
    {
        "name_en": "Laboratory Tests",
        "description_en": "Blood work and urinalysis",
        "name_tr": "Laboratuvar Testleri",
        "description_tr": "Kan ve idrar testleri",
        "name_nl": "Laboratoriumonderzoek",
        "description_nl": "Bloed- en urineonderzoek",
        "name_fi": "Laboratoriotutkimukset",
        "description_fi": "Veri- ja virtsakokeet",
    },
    {
        "name_en": "Limping / Mobility Issues",
        "description_en": "Joint pain or difficulty walking",
        "name_tr": "Topallama / Hareket Sorunu",
        "description_tr": "Eklem ağrısı veya yürüme zorluğu",
        "name_nl": "Kreupelheid / Mobiliteitsproblemen",
        "description_nl": "Gewrichtspijn of loopproblemen",
        "name_fi": "Ontuminen / Liikkumisongelmat",
        "description_fi": "Nivelkipu tai kävelyvaikeus",
    },
    {
        "name_en": "Microchipping",
        "description_en": "Permanent identification implant",
        "name_tr": "Mikroçip",
        "description_tr": "Kalıcı kimlik çipi",
        "name_nl": "Chippen",
        "description_nl": "Permanente identificatiechip",
        "name_fi": "Mikrosirutus",
        "description_fi": "Pysyvä tunnistesiru",
    },
    {
        "name_en": "Nutrition Consultation",
        "description_en": "Diet and weight management",
        "name_tr": "Beslenme Danışmanlığı",
        "description_tr": "Diyet ve kilo yönetimi",
        "name_nl": "Voedingsadvies",
        "description_nl": "Dieet- en gewichtsbeheer",
        "name_fi": "Ravitsemusneuvonta",
        "description_fi": "Ruokavalio ja painonhallinta",
    },
    {
        "name_en": "Pregnancy Checkup",
        "description_en": "Prenatal care",
        "name_tr": "Gebelik Kontrolü",
        "description_tr": "Doğum öncesi bakım",
        "name_nl": "Drachtcontrole",
        "description_nl": "Prenatale zorg",
        "name_fi": "Tiineystarkastus",
        "description_fi": "Sikiöaikainen hoito",
    },
    {
        "name_en": "Preventive Care",
        "description_en": "General health and prevention services",
        "name_tr": "Koruyucu Bakım",
        "description_tr": "Genel sağlık ve hastalık önleme hizmetleri",
        "name_nl": "Preventieve Zorg",
        "description_nl": "Algemene gezondheidszorg en preventie",
        "name_fi": "Ennaltaehkäisevä hoito",
        "description_fi": "Yleinen terveydenhuolto ja ennaltaehkäisy",
    },
    {
        "name_en": "Puppy / Kitten Checkup",
        "description_en": "Initial examination for young pets",
        "name_tr": "Yavru Kontrolü",
        "description_tr": "Yavru hayvan için ilk muayene",
        "name_nl": "Puppy / Kitten Controle",
        "description_nl": "Eerste onderzoek van jonge dieren",
        "name_fi": "Pennun / kissanpennun tarkastus",
        "description_fi": "Nuoren lemmikin ensimmäinen tutkimus",
    },
    {
        "name_en": "Respiratory Problems",
        "description_en": "Coughing, sneezing, or breathing difficulty",
        "name_tr": "Solunum Problemleri",
        "description_tr": "Öksürük, hapşırma veya nefes zorluğu",
        "name_nl": "Ademhalingsproblemen",
        "description_nl": "Hoesten, niezen of ademhalingsproblemen",
        "name_fi": "Hengitysongelmat",
        "description_fi": "Yskä, aivastelu tai hengitysvaikeudet",
    },
    {
        "name_en": "Senior Pet Wellness",
        "description_en": "Geriatric health assessment",
        "name_tr": "Yaşlı Hayvan Kontrolü",
        "description_tr": "Geriatrik sağlık değerlendirmesi",
        "name_nl": "Senior Huisdier Controle",
        "description_nl": "Gezondheidscontrole voor oudere dieren",
        "name_fi": "Seniorieläimen tarkastus",
        "description_fi": "Ikääntyvän lemmikin terveystarkastus",
    },
    {
        "name_en": "Skin Problems",
        "description_en": "Itching, rashes, hair loss, and allergies",
        "name_tr": "Cilt Problemleri",
        "description_tr": "Kaşıntı, döküntü, tüy dökülmesi ve alerjiler",
        "name_nl": "Huidproblemen",
        "description_nl": "Jeuk, uitslag, haaruitval en allergieën",
        "name_fi": "Iho-ongelmat",
        "description_fi": "Kutina, ihottuma, karvanlähtö ja allergiat",
    },
    {
        "name_en": "Spay / Neuter",
        "description_en": "Sterilization surgery",
        "name_tr": "Kısırlaştırma",
        "description_tr": "Üreme kontrolü ameliyatı",
        "name_nl": "Sterilisatie / Castratie",
        "description_nl": "Onvruchtbaarmakende operatie",
        "name_fi": "Sterilointi",
        "description_fi": "Lisääntymisen estoleikkaus",
    },
    {
        "name_en": "Tooth Extraction",
        "description_en": "Removal of damaged teeth",
        "name_tr": "Diş Çekimi",
        "description_tr": "Hasarlı dişlerin alınması",
        "name_nl": "Tandextractie",
        "description_nl": "Verwijderen van beschadigde tanden",
        "name_fi": "Hampaan poisto",
        "description_fi": "Vaurioituneen hampaan poisto",
    },
    {
        "name_en": "Travel / Passport Preparation",
        "description_en": "Documents and health checks for traveling abroad",
        "name_tr": "Seyahat / Pasaport Hazırlığı",
        "description_tr": "Yurt dışı seyahat için belge ve sağlık kontrolleri",
        "name_nl": "Reis- / Paspoortvoorbereiding",
        "description_nl": "Documenten en gezondheidscontroles voor reizen naar het buitenland",
        "name_fi": "Matkustus / Passivalmistelu",
        "description_fi": "Ulkomaanmatkailuun tarvittavat asiakirjat ja terveystarkastukset",
    },
    {
        "name_en": "Tumor Removal",
        "description_en": "Growth or mass removal",
        "name_tr": "Tümör Alınması",
        "description_tr": "Kitle veya tümörün çıkarılması",
        "name_nl": "Tumorverwijdering",
        "description_nl": "Verwijderen van gezwel of massa",
        "name_fi": "Kasvaimen poisto",
        "description_fi": "Kasvaimen tai kyhmyn poisto",
    },
    {
        "name_en": "Urinary Issues",
        "description_en": "Frequent urination, blood in urine, or straining",
        "name_tr": "İdrar Problemleri",
        "description_tr": "Sık idrara çıkma, idrarda kan veya zorlanma",
        "name_nl": "Urineproblemen",
        "description_nl": "Vaak plassen, bloed in urine of persen",
        "name_fi": "Virtsaamisongelmat",
        "description_fi": "Tiheä virtsaaminen, veri tai ponnistelu",
    },
    {
        "name_en": "Vaccination",
        "description_en": "Core vaccines such as rabies, distemper, and parvovirus",
        "name_tr": "Aşılama",
        "description_tr": "Kuduz, gençlik ve parvo gibi temel aşılar",
        "name_nl": "Vaccinatie",
        "description_nl": "Basisvaccins zoals rabiës en parvo",
        "name_fi": "Rokotus",
        "description_fi": "Perusrokotukset kuten raivotauti ja parvo",
    },
    {
        "name_en": "Wound Treatment",
        "description_en": "Cuts, bite wounds, or injuries",
        "name_tr": "Yara Tedavisi",
        "description_tr": "Kesik, ısırık veya yaralanmalar",
        "name_nl": "Wondbehandeling",
        "description_nl": "Snijwonden, beten of letsels",
        "name_fi": "Haavan hoito",
        "description_fi": "Haavat, puremat tai vammat",
    },
]


class Command(BaseCommand):
    help = 'Seed AppointmentReason data with translations (EN, TR, NL, FI)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing appointment reasons before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = AppointmentReason.objects.count()
            AppointmentReason.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Deleted {count} existing appointment reasons.')
            )

        created_count = 0
        updated_count = 0

        for order, reason_data in enumerate(APPOINTMENT_REASONS, start=1):
            # Use English name as the primary lookup key
            name_en = reason_data['name_en']
            
            # Prepare the data for update_or_create
            defaults = {
                'order': order,
                'is_active': True,
                # English
                'name_en': name_en,
                'description_en': reason_data['description_en'],
                # Turkish
                'name_tr': reason_data['name_tr'],
                'description_tr': reason_data['description_tr'],
                # Dutch
                'name_nl': reason_data['name_nl'],
                'description_nl': reason_data['description_nl'],
                # Finnish
                'name_fi': reason_data['name_fi'],
                'description_fi': reason_data['description_fi'],
            }

            reason, created = AppointmentReason.objects.update_or_create(
                name_en=name_en,
                defaults=defaults
            )

            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created: {name_en}')
            else:
                updated_count += 1
                self.stdout.write(f'  ↻ Updated: {name_en}')

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Done! Created: {created_count}, Updated: {updated_count}, '
                f'Total: {AppointmentReason.objects.count()}'
            )
        )
