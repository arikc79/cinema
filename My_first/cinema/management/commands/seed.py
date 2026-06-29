import urllib.request
from django.contrib.auth.models import User, Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from cinema.models import Movie, Session, UserProfile

MOVIES = [
    {
        "title": "The Shawshank Redemption",
        "year": 1994,
        "duration": 142,
        "genre": "drama",
        "description": (
            "Two imprisoned men bond over a number of years, finding solace and "
            "eventual redemption through acts of common decency."
        ),
        "imdb": "tt0111161",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg",
    },
    {
        "title": "The Godfather",
        "year": 1972,
        "duration": 175,
        "genre": "drama",
        "description": (
            "The aging patriarch of an organized crime dynasty transfers control of "
            "his clandestine empire to his reluctant son."
        ),
        "imdb": "tt0068646",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
    },
    {
        "title": "The Dark Knight",
        "year": 2008,
        "duration": 152,
        "genre": "action",
        "description": (
            "When the menace known as the Joker wreaks havoc and chaos on the people "
            "of Gotham, Batman must accept one of the greatest psychological and physical "
            "tests of his ability to fight injustice."
        ),
        "imdb": "tt0468569",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg",
    },
    {
        "title": "Pulp Fiction",
        "year": 1994,
        "duration": 154,
        "genre": "thriller",
        "description": (
            "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair "
            "of diner bandits intertwine in four tales of violence and redemption."
        ),
        "imdb": "tt0110912",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
    },
    {
        "title": "Inception",
        "year": 2010,
        "duration": 148,
        "genre": "sci-fi",
        "description": (
            "A thief who steals corporate secrets through the use of dream-sharing "
            "technology is given the inverse task of planting an idea into the mind "
            "of a C.E.O."
        ),
        "imdb": "tt1375666",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg",
    },
    {
        "title": "Fight Club",
        "year": 1999,
        "duration": 139,
        "genre": "drama",
        "description": (
            "An insomniac office worker and a devil-may-care soap maker form an "
            "underground fight club that evolves into something much, much more."
        ),
        "imdb": "tt0137523",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BNDIzNDU0YzEtYzE5Ni00ZjlkLTk5ZjgtNjM3NWE4YzA3Nzk3XkEyXkFqcGdeQXVyMjUzOTY1NTc@._V1_SX300.jpg",
    },
    {
        "title": "Interstellar",
        "year": 2014,
        "duration": 169,
        "genre": "sci-fi",
        "description": (
            "A team of explorers travel through a wormhole in space in an attempt "
            "to ensure humanity's survival."
        ),
        "imdb": "tt0816692",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
    },
    {
        "title": "The Matrix",
        "year": 1999,
        "duration": 136,
        "genre": "sci-fi",
        "description": (
            "When a beautiful stranger leads computer hacker Neo to a forbidding "
            "underworld, he discovers the shocking truth — the life he knows is the "
            "elaborate deception of an evil cyber-intelligence."
        ),
        "imdb": "tt0133093",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVlLTM5YTUtZmJhOWEzMDkxOGEwXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
    },
    {
        "title": "Goodfellas",
        "year": 1990,
        "duration": 146,
        "genre": "drama",
        "description": (
            "The story of Henry Hill and his life in the mob, covering his relationship "
            "with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVito "
            "in the New York area from the 1950s to the 1980s."
        ),
        "imdb": "tt0099685",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BY2NkZjEzMDItZTVmMi00YzE3LWI1YjctMmY2ODI0OTk3ZTY5XkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
    },
    {
        "title": "The Silence of the Lambs",
        "year": 1991,
        "duration": 118,
        "genre": "thriller",
        "description": (
            "A young F.B.I. cadet must receive the help of an incarcerated and "
            "manipulative cannibal killer to help catch another serial killer, "
            "a madman who skins his victims."
        ),
        "imdb": "tt0102926",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BNjNhZTk0ZmEtNjJhMi00YzFlLWE1MmEtYzM1M2ZmMGMwMTU4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
    },
]


def download_poster(url, filename):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return ContentFile(resp.read(), name=filename)
    except Exception:
        return None


class Command(BaseCommand):
    help = "Seed the database with movies, admin user, and worker group"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-posters",
            action="store_true",
            help="Skip downloading posters",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear all movies before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Movie.objects.all().delete()
            self.stdout.write("Cleared all movies.")

        # Admin user
        admin, created_admin = User.objects.get_or_create(username="admin")
        admin.email = "admin@cinema.local"
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("admin1234")
        admin.save()
        UserProfile.objects.get_or_create(user=admin)
        self.stdout.write(self.style.SUCCESS("Admin ready: admin / admin1234"))

        # Worker group
        worker_group, _ = Group.objects.get_or_create(name="Робітник")

        # Demo worker
        if not User.objects.filter(username="worker").exists():
            worker = User.objects.create_user("worker", password="worker1234")
            worker.groups.add(worker_group)
            UserProfile.objects.get_or_create(user=worker)
            self.stdout.write(self.style.SUCCESS("Created worker / worker1234"))

        # Movies
        created = 0
        for data in MOVIES:
            movie, new = Movie.objects.get_or_create(
                title=data["title"],
                year=data["year"],
                defaults={
                    "duration": data["duration"],
                    "genre": data["genre"],
                    "description": data["description"],
                },
            )
            # Always ensure poster_url is set (works for existing movies too)
            if not movie.poster_url and data.get("poster_url"):
                movie.poster_url = data["poster_url"]
                movie.save(update_fields=["poster_url"])

            if new:
                if not options["no_posters"]:
                    poster_file = download_poster(
                        data["poster_url"], f"poster_{data['imdb']}.jpg"
                    )
                    if poster_file:
                        movie.poster.save(poster_file.name, poster_file, save=True)
                        self.stdout.write(f"  + {movie.title} (poster + url)")
                    else:
                        self.stdout.write(f"  + {movie.title} (url only)")
                else:
                    self.stdout.write(f"  + {movie.title} (url only)")
                created += 1
            else:
                self.stdout.write(f"  = {movie.title} (already exists)")

        self.stdout.write(self.style.SUCCESS(f"\nDone. {created} movies added."))
