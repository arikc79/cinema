from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta


class Movie(models.Model):
    """Модель для фільмів"""
    GENRE_CHOICES = [
        ('action', 'Бойовик'),
        ('comedy', 'Комедія'),
        ('drama', 'Драма'),
        ('horror', 'Жахи'),
        ('fantasy', 'Фентезі'),
        ('sci-fi', 'Наукова фантастика'),
        ('thriller', 'Трилер'),
        ('romance', 'Романтика'),
        ('animation', 'Анімація'),
        ('documentary', 'Документальний'),
    ]

    title = models.CharField(max_length=200, verbose_name='Назва фільму')
    description = models.TextField(verbose_name='Опис')
    year = models.IntegerField(
        verbose_name='Рік випуску',
        validators=[MinValueValidator(1895), MaxValueValidator(2100)]
    )
    duration = models.IntegerField(
        verbose_name='Тривалість (хв)',
        validators=[MinValueValidator(1)]
    )
    genre = models.CharField(
        max_length=20,
        choices=GENRE_CHOICES,
        verbose_name='Жанр'
    )
    poster = models.ImageField(
        upload_to='posters/',
        blank=True,
        null=True,
        verbose_name='Постер'
    )
    poster_url = models.URLField(blank=True, default='', verbose_name='URL постера')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Фільм'
        verbose_name_plural = 'Фільми'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.year})"

    def get_absolute_url(self):
        return reverse('movie_detail', kwargs={'pk': self.pk})

    def average_rating(self):
        """Середня оцінка фільму"""
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0


class Session(models.Model):
    """Модель для сеансів фільмів"""
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='Фільм'
    )
    date = models.DateTimeField(verbose_name='Дата та час сеансу')
    hall_number = models.IntegerField(
        verbose_name='Номер зали',
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    max_tickets = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        verbose_name='Кількість місць'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеанси'
        ordering = ['date']

    def __str__(self):
        return f"{self.movie.title} - {self.date.strftime('%d.%m.%Y %H:%M')} (Зала {self.hall_number})"

    def clean(self):
        super().clean()

        # Якщо сеанс ще без фільму/дати, відкладемо перевірку до повного заповнення.
        if not self.movie_id or not self.date:
            return

        new_start = self.date
        new_end = new_start + timedelta(minutes=self.movie.duration)

        same_hall_sessions = (
            Session.objects.filter(hall_number=self.hall_number)
            .exclude(pk=self.pk)
            .select_related('movie')
        )

        for existing_session in same_hall_sessions:
            existing_start = existing_session.date
            existing_end = existing_start + timedelta(minutes=existing_session.movie.duration)

            # Перетин інтервалів: [start, end)
            if existing_start < new_end and existing_end > new_start:
                raise ValidationError(
                    {'date': 'У вибраній залі час сеансу перетинається з іншим фільмом.'}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def booked_tickets(self):
        return self.bookings.aggregate(total=Sum('tickets_count')).get('total') or 0

    def available_tickets(self):
        return max(self.max_tickets - self.booked_tickets(), 0)


class Review(models.Model):
    """Модель для відгуків на фільми"""
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Фільм'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Користувач'
    )
    text = models.TextField(verbose_name='Текст відгуку')
    rating = models.IntegerField(
        verbose_name='Оцінка',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')

    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        ordering = ['-created_at']
        # Один користувач - один відгук на фільм
        unique_together = ('movie', 'user')

    def __str__(self):
        return f"Відгук від {self.user.username} на {self.movie.title} - {self.rating}/10"

    def get_absolute_url(self):
        return reverse('movie_detail', kwargs={'pk': self.movie.pk})

    def author_avatar_url(self):
        if hasattr(self.user, 'profile') and self.user.profile.avatar:
            return self.user.profile.avatar.url
        return ''


class UserProfile(models.Model):
    """Розширений профіль користувача"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Користувач'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Фото профілю'
    )

    class Meta:
        verbose_name = 'Профіль користувача'
        verbose_name_plural = 'Профілі користувачів'

    def __str__(self):
        return f"Профіль: {self.user.username}"


class FavoriteMovie(models.Model):
    """Улюблені фільми користувача"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_movies',
        verbose_name='Користувач'
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Фільм'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Улюблений фільм'
        verbose_name_plural = 'Улюблені фільми'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'movie'], name='unique_favorite_movie')
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.movie.title}"


class TicketBooking(models.Model):
    """Бронювання квитків на сеанс"""
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Сеанс'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ticket_bookings',
        verbose_name='Користувач'
    )
    tickets_count = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Кількість квитків'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_watched = models.BooleanField(default=False, verbose_name='Переглянуто')
    watched_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата позначки перегляду')

    class Meta:
        verbose_name = 'Бронювання'
        verbose_name_plural = 'Бронювання'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['session', 'user'], name='unique_user_booking_per_session')
        ]

    def __str__(self):
        return f"{self.user.username}: {self.session} ({self.tickets_count})"

    def clean(self):
        super().clean()
        if self.session_id and self.session.date < timezone.now() and not self.pk:
            raise ValidationError({'session': 'Не можна бронювати квитки на минулий сеанс.'})

        if self.session_id:
            reserved_by_others = self.session.bookings.exclude(pk=self.pk).aggregate(total=Sum('tickets_count')).get('total') or 0
            if reserved_by_others + self.tickets_count > self.session.max_tickets:
                raise ValidationError(
                    {'tickets_count': 'Недостатньо вільних місць у залі для цього сеансу.'}
                )

    def mark_watched(self):
        self.is_watched = True
        self.watched_at = timezone.now()
        self.save(update_fields=['is_watched', 'watched_at'])
