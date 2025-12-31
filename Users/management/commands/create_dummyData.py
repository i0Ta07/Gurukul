from django.core.management.base import BaseCommand
from Users.models import *


class Command(BaseCommand):
    help = 'Create dummy data'

    def handle(self, *args, **options):
       
        # Users
        users_data = [
            {
                "is_staff": True,
                "is_active": True,
                "is_superuser": True,
                "password": "pbkdf2_sha256$870000$oQ95vNSZwNgo0a9M2wlQr7$clQ+CUzcfvo76opJwJ2T3JrI1CxrhKPGKm16rb9V7Io=",
                "username": "i0Ta",
                "first_name": "Rohit",
                "last_name": "Sharma",
                "email": "rohitsharmaa2510@gmail.com",
                "title": "Mr.",
                "phone_number": "9315258404",
                "date_of_birth": "2003-06-10",
                "user_type": "student",
            },
            {
                "is_staff": False,
                "is_active": True,
                "is_superuser": False,
                "username": "ankit_shahi",
                "first_name": "Ankit",
                "last_name": "Shahi",
                "password": "pbkdf2_sha256$870000$LTCl18QsDzqrs1oVUp7AMg$27g81PAPQoM8Q3ZtBQ4PB0igAwwZz9a/652y0uucvsE=",
                "title": "Mr.",
                "phone_number": "1234567890",
                "date_of_birth": "1985-05-15",
                "user_type": "student",
                "email": "ankit_shahi@gmail.com"
            },
            {
                "is_staff": False,
                "is_active": True,
                "is_superuser": False,
                "username": "rajeev_sharma",
                "first_name": "Rajeev",
                "last_name": "Sharma",
                "password": "pbkdf2_sha256$870000$LTCl18QsDzqrs1oVUp7AMg$27g81PAPQoM8Q3ZtBQ4PB0igAwwZz9a/652y0uucvsE=",
                "title": "Mr.",
                "phone_number": "5471258236",
                "date_of_birth": "2002-08-25",
                "user_type": "teacher",
                "email": "rajeev_sharma@example.com"
            },
            {
                "is_staff": False,
                "is_active": True,
                "is_superuser": False,
                "username": "nirmesh_sharma",
                "first_name": "Nirmesh",
                "last_name": "Sharma",
                "password": "pbkdf2_sha256$870000$LTCl18QsDzqrs1oVUp7AMg$27g81PAPQoM8Q3ZtBQ4PB0igAwwZz9a/652y0uucvsE=",
                "title": "Mrs.",
                "phone_number": "8125823622",
                "date_of_birth": "1985-08-25",
                "user_type": "teacher",
                "email": "nirmesh_sharma@example.com"
            },
            {
                "password": "pbkdf2_sha256$870000$app6E0rc3pFH17mziJKeHS$dJteNFC/Ow6yt2E9FBuzd8Cj1K7bgLmsotHZpj+OGpw=",
                "is_superuser": True,
                "username": "nidhi",
                "first_name": "Nidhi",
                "last_name": "Sharma",
                "email": "nidhisharma@gmail.com",
                "is_staff": True,
                "is_active": True,
                "title": "Ms.",
                "phone_number": "9625182811",
                "date_of_birth": "2000-03-25",
                "user_type": "teacher",
            },
            {
                "password": "pbkdf2_sha256$870000$kJn8T8UTNMyBG7cb8UaEKD$dMMf1mrc4sn5o+7uW2NGS0FjXff3WITzglpE7J5IfR4=",
                "is_superuser": False,
                "username": "ayush_sharma",
                "first_name": "Ayush",
                "last_name": "Sharma",
                "email": "ayush_sharma@gmail.com",
                "is_staff": False,
                "is_active": True,
                "title": "Mr.",
                "phone_number": "5841269748",
                "date_of_birth": "2007-06-20",
                "user_type": "student",
            }
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(username=user_data["username"], defaults=user_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f"User {user.username} created successfully!"))
            else:
                self.stdout.write(self.style.WARNING(f"User {user.username} already exists."))
        #books
        books = [
            {
                "name": "A Thousand Splendid Suns",
                "author": "Khaled Hosseini",
                "edition": "FOURTH",
                "publisher": "Bloomsbury",
                "isbn": "1429514604",
                "genre": "Drama, Fiction, History",
                "language": "English",
                "num_pages": 253,
                "cover_image": "book_covers/81xIPfJ6iUL.jpg",
                "file": "book_files/a_thousand_splendid_sun.pdf",
                "created_by":  User.objects.get(id=41),
                "access_type": "PUBLIC",
                "access_code": "",
                "book_saved_by_users": [42,41] #used as temp will be popped before creation of the book
            },
                        {
                "name": "The Kite Runner",
                "author": "Khaled Hosseini",
                "edition": "FOURTH",
                "publisher": "Bloomsbury",
                "isbn": "5425896215822",
                "genre": "History, Friendship",
                "language": "English",
                "num_pages": 374,
                "cover_image": "book_covers/the_kite_runner.jpg",
                "file": "book_files/the_kite_runner.pdf",
                "created_by": 41,
                "access_type": "PUBLIC",
                "access_code": "",
                "book_saved_by_users": [42]
            },
            {
                "name": "Operating System Concepts",
                "author": "Abraham Silberschatz, Peter Baer Galvin, Greg Gagne",
                "edition": "Fifth",
                "publisher": "Wiley Publications",
                "isbn": "9781118063330",
                "genre": "Textbook",
                "language": "English",
                "num_pages": 944,
                "cover_image": "book_covers/83833.jpg",
                "file": "book_files/Abraham_Silberschatz-Operating_System_Concepts_9th2012_12.pdf",
                "created_by": 42,
                "access_type": "PUBLIC",
                "access_code": "",
                "book_saved_by_users": [42, 41]
            },
            {
                "name": "Data Communication and Networking",
                "author": "Behrouz A. Forouzan",
                "edition": "FIFTH",
                "publisher": "McGraw Hill",
                "isbn": "9780073376226",
                "genre": "Textbook",
                "language": "English",
                "num_pages": 1269,
                "cover_image": "book_covers/61Wplu0FrwL._AC_UF10001000_QL80_.jpg",
                "file": "book_files/Data-Communications-and-Network-5e.pdf",
                "created_by": 42,
                "access_type": "PUBLIC",
                "access_code": "",
                "book_saved_by_users": [41]
            },
            {
                "name": "The Complete Reference - Java",
                "author": "Herbert Schildt",
                "edition": "Ninth",
                "publisher": "Oracle Press",
                "isbn": "9780071808569",
                "genre": "Textbook",
                "language": "English",
                "num_pages": 1313,
                "cover_image": "book_covers/java-the-complete-reference-original-imafyw4smeydeqbn.jpeg",
                "file": "book_files/Herbert_Schildt_Java_-_The_Complete_Reference_Oracle_Press_9th_Edition_2014.pdf",
                "created_by": 42,
                "access_type": "PUBLIC",
                "access_code": "",
                "book_saved_by_users": [41]
            }

        ]

        for book_data in books:
            saved_by_users = book_data.pop("book_saved_by_users")  # Explicitly pop the saved users list
            book, created = Book.objects.get_or_create(name=book_data["name"], defaults=book_data)

            # Set ManyToManyField dynamically
            book.book_saved_by_users.set(User.objects.filter(id__in=saved_by_users))  

            if created:
                self.stdout.write(self.style.SUCCESS(f"Book {book.name} created successfully!"))
            else:
                self.stdout.write(self.style.WARNING(f"Book {book.name} already exists."))


       # Processed list of class data
        classes = [
            {
                "name": "MCA-2A",
                "created_by": User.objects.get(id=42),
                "description": "2024-2026 batch, VIPS",
                "current_topic": "Heaps",
                "last_topic": "Semaphores",
                "next_topic": "BS on Answers",
                "next_class_date": "2025-03-31T12:30:00Z",
                "next_class_teacher": User.objects.get(id=42),
                "max_students": 30,
                "is_active": True,
                "syllabus_file": "syllabus_files/MCA-2A.pdf",
                "access_type": "public",
                "access_code": "",
                "textbooks": [
                    "TB1. E. Horowitz and S. Sahni, ôFundamentals of Data Structures in Cö. Universities Press, Second edition, 2008.",
                    "TB2. Mark Allen Weiss, ôData Structures and Algorithm Analysis in C++ö, Pearson Education India, Fourth Edition, 2014.",
                    "TB3. Mary E. S. Loomis, ôData Management and File Structureö, PHI, Second Edition, 2009."
                ],
                "schedule": ["9 AM", "10 AM", "None", "5 PM", "12 PM", "2 PM", "None"],
                "students": [87, 101, 41],
                "teachers": [42]
            },
            {
                "name": "Java Programming",
                "created_by": User.objects.get(id=88),
                "description": "Java Intermediate Classes,2024-25 batch",
                "current_topic": "User Exception Handling",
                "last_topic": "JDBC",
                "next_topic": "AWT an Swing",
                "next_class_date": "2025-04-23T11:30:00Z",
                "next_class_teacher": User.objects.get(id=42),
                "max_students": 30,
                "is_active": True,
                "syllabus_file": "syllabus_files/java_syllabus.pdf",
                "access_type": "public",
                "access_code": "",
                "textbooks": [
                    "TB1. Herbert Schildt, ôJava - The Complete Referenceö, Oracle Press, 9th Edition, 2014.",
                    "TB2. Kathy Sierra and BertBates, ôHead First Javaö, OÆReilly Publications, 2nd Edition, 2005."
                ],
                "schedule": ["8 AM", "5 PM", "None", "2 PM", "6 PM", "10 AM", "None"],
                "students": [87, 41],
                "teachers": [42, 89, 88]
            },
            {
                "name": "English Lit",
                "created_by": User.objects.get(id=88),
                "description": "Your mind is free, such as you life",
                "current_topic": "Russian Novelists",
                "last_topic": "Post-war Tragedies",
                "next_topic": "Modern Art",
                "next_class_date": "2025-03-26T18:30:00Z",
                "next_class_teacher": User.objects.get(id=88),
                "max_students": 30,
                "is_active": True,
                "syllabus_file": "syllabus_files/goodreads_100_books_you_should_read_in_a_lifetime.pdf",
                "access_type": "public",
                "access_code": "",
                "textbooks": [
                    "The Kite Runner",
                    "Crime and Punishment",
                    "White Nights"
                ],
                "schedule": ["9 AM", "None", "12 PM", "2 PM", "None", "10 AM", "None"],
                "students": [87, 41],
                "teachers": [89, 88]
            }
        ]

        # Loop through and process the class data
        for class_data in classes:
            students = class_data.pop("students")  # Remove students list before creation
            teachers = class_data.pop("teachers")  # Remove teachers list before creation
            textbooks = class_data.pop("textbooks")  # Remove textbooks list before creation
            schedule = class_data.pop("schedule")  # Remove schedule list before creation

            # Create or get the class instance
            class_instance, created = Class.objects.get_or_create(name=class_data["name"], defaults=class_data)

            # Set ManyToMany fields dynamically
            class_instance.students.set(User.objects.filter(id__in=students))
            class_instance.teachers.set(User.objects.filter(id__in=teachers))
            class_instance.textbooks = textbooks
            class_instance.schedule = schedule
            class_instance.save()  # Save after updating fields

            if created:
                print(f"Class {class_instance.name} created successfully!")
            else:
                print(f"Class {class_instance.name} already exists.")
