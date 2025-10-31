from django.core.management.base import BaseCommand
from userapp.models import CustomUser, Profile


class Command(BaseCommand):
    help = 'Create 7 sample users with Netherlands-based profiles'

    def handle(self, *args, **options):
        users_data = [
            {
                "email": "sophie.jansen@gmail.com",
                "password": "S0phie!2025",
                "first_name": "Sophie",
                "last_name": "Jansen",
                "phone": "+31 6 4123 5678",
                "address": "Keizersgracht 112",
                "city": "Amsterdam",
                "zip_code": "1015 AB",
                "country": "Netherlands"
            },
            {
                "email": "maarten.vanleeuwen@outlook.com",
                "password": "MVaL#9876",
                "first_name": "Maarten",
                "last_name": "van Leeuwen",
                "phone": "+31 6 2334 1122",
                "address": "Lijnbaan 45",
                "city": "Rotterdam",
                "zip_code": "3012 CD",
                "country": "Netherlands"
            },
            {
                "email": "laura.dewit@ziggo.nl",
                "password": "LdW!2024pass",
                "first_name": "Laura",
                "last_name": "de Wit",
                "phone": "+31 70 312 5544",
                "address": "Prinsestraat 8",
                "city": "The Hague",
                "zip_code": "2513 EF",
                "country": "Netherlands"
            },
            {
                "email": "thijs.bosman@yahoo.com",
                "password": "Th!jsB0s#1",
                "first_name": "Thijs",
                "last_name": "Bosman",
                "phone": "+31 30 654 7788",
                "address": "Oudegracht 203",
                "city": "Utrecht",
                "zip_code": "3511 GH",
                "country": "Netherlands"
            },
            {
                "email": "inge.peeters@company.nl",
                "password": "IngeP@2025",
                "first_name": "Inge",
                "last_name": "Peeters",
                "phone": "+31 40 233 9900",
                "address": "Stratumseind 12",
                "city": "Eindhoven",
                "zip_code": "5611 IJ",
                "country": "Netherlands"
            },
            {
                "email": "wouter.hendriks@proton.me",
                "password": "Wout3rHend!kS",
                "first_name": "Wouter",
                "last_name": "Hendriks",
                "phone": "+31 50 312 2233",
                "address": "Akerkhof 4",
                "city": "Groningen",
                "zip_code": "9712 KL",
                "country": "Netherlands"
            },
            {
                "email": "emma.vandam@gmail.com",
                "password": "EmmaVD@#55",
                "first_name": "Emma",
                "last_name": "van Dam",
                "phone": "+31 23 542 1100",
                "address": "Grote Markt 2",
                "city": "Haarlem",
                "zip_code": "2011 MN",
                "country": "Netherlands"
            },
            {
                "email": "jeroen.smits@nlstartup.com",
                "password": "JSm1ts!Start",
                "first_name": "Jeroen",
                "last_name": "Smits",
                "phone": "+31 43 321 7788",
                "address": "Vrijthof 18",
                "city": "Maastricht",
                "zip_code": "6211 OP",
                "country": "Netherlands"
            },
            {
                "email": "liesbeth.kok@icloud.com",
                "password": "LKok2025$secure",
                "first_name": "Liesbeth",
                "last_name": "Kok",
                "phone": "+31 71 512 3344",
                "address": "Breestraat 60",
                "city": "Leiden",
                "zip_code": "2311 QR",
                "country": "Netherlands"
            },
            {
                "email": "niels.verhoeven@hotmail.com",
                "password": "N!elsV#890",
                "first_name": "Niels",
                "last_name": "Verhoeven",
                "phone": "+31 24 356 4410",
                "address": "Houtstraat 27",
                "city": "Nijmegen",
                "zip_code": "6511 ST",
                "country": "Netherlands"
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS('[START] Creating sample users for FAMMO...'))
        self.stdout.write("="*60 + "\n")
        
        for user_data in users_data:
            email = user_data['email']
            
            # Check if user already exists
            if CustomUser.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"[SKIP] User {email} already exists. Skipping..."))
                skipped_count += 1
                continue
            
            try:
                # Create the user
                user = CustomUser.objects.create_user(
                    email=email,
                    password=user_data['password']
                )
                user.is_active = True
                user.save()
                
                # Create the profile
                profile = Profile.objects.create(
                    user=user,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone=user_data['phone'],
                    address=user_data['address'],
                    city=user_data['city'],
                    zip_code=user_data['zip_code'],
                    country=user_data['country'],
                )
                
                self.stdout.write(self.style.SUCCESS(
                    f"[OK] Created user: {user_data['first_name']} {user_data['last_name']} ({email})"
                ))
                created_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[ERROR] Error creating user {email}: {str(e)}"))
                skipped_count += 1
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"Successfully created: {created_count} users"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count} users"))
        self.stdout.write("="*60)
        self.stdout.write(self.style.NOTICE("\nLogin credentials for all users:"))
        self.stdout.write("  Password: TestPass123!")
        self.stdout.write("  Emails: Check the list above\n")