from sqlalchemy import create_engine, delete
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from app.modules.bookings.models import Booking, BookingSeat
from app.modules.screens.models import Screen
from app.modules.theaters.models import Theater
from app.modules.movies.models import Movie, MovieStatus
from app.modules.seats.models import Seat, SeatTypeEnum
from app.core.config import settings
from datetime import datetime, timedelta, timezone
from app.modules.shows.models import Show
from uuid import uuid4
from app.modules.auth.models import User, UserRole
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from fastapi import HTTPException
from app.modules.bookings.schemas import BookingCreate
from app.modules.bookings.service import create_booking
from sqlalchemy import func, select



def make_test_session_factory():
    if settings.TEST_DATABASE_URL is None:
        raise RuntimeError("TEST_DATABASE_URL is missing")

    test_url = settings.TEST_DATABASE_URL.get_secret_value()
    test_db = make_url(test_url).database
    demo_db = make_url(settings.DATABASE_URL).database

    if test_db != "cinebook_test" or test_db == demo_db:
        raise RuntimeError("Expected a separate cinebook_test database")

    test_engine = create_engine(test_url)
    return sessionmaker(bind=test_engine)


def seed_booking_scenario(session_factory):
    with session_factory() as db:
        theater = Theater(
            name="Concurrency Test Theater",
            address="123 Test Road",
            city="Ahmedabad",
            timezone="Asia/Kolkata",
        )
        db.add(theater)
        db.flush()

        screen = Screen(theater_id=theater.id, name="Screen 1")
        db.add(screen)
        db.flush()

        seat = Seat(
            screen_id=screen.id,
            row_label="A",
            seat_number=1,
            seat_type=SeatTypeEnum.REGULAR,
        )

        movie = Movie(
            title="Concurrency Test Movie",
            duration_minutes=120,
            status=MovieStatus.PUBLISHED,
        )

        db.add_all([seat, movie])
        db.flush()

        show = Show(
            movie_id=movie.id,
            screen_id=screen.id,
            starts_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db.add(show)
        db.flush()

        customer_a = User(
            email=f"customer_a_{uuid4().hex}@example.com",
            password_hash="hashed_password",
            role=UserRole.CUSTOMER,
        )

        customer_b = User(
            email=f"customer_b_{uuid4().hex}@example.com",
            password_hash="hashed_password2",
            role=UserRole.CUSTOMER,
        )

        db.add_all([customer_a, customer_b])
        db.flush()

        scenario = (
            show.id,
            seat.id,
            customer_a.id,
            customer_b.id,
            theater.id,
            screen.id,
            movie.id,
        )

        db.commit()

        return scenario

def cleanup_booking_scenario(session_factory, scenario):
    show_id, seat_id, customer_a_id, customer_b_id, theater_id, screen_id, movie_id = scenario

    with session_factory.begin() as db:
        booking_ids = select(Booking.id).where(
            Booking.show_id == show_id,
            Booking.user_id.in_([customer_a_id, customer_b_id])
        )

        db.execute(delete(BookingSeat).where(BookingSeat.booking_id.in_(booking_ids)))
        db.execute(delete(Booking).where(Booking.id.in_(booking_ids)))
        db.execute(delete(Show).where(Show.id == show_id))
        db.execute(delete(Seat).where(Seat.id == seat_id))
        db.execute(delete(Screen).where(Screen.id == screen_id))
        db.execute(delete(Theater).where(Theater.id == theater_id))
        db.execute(delete(Movie).where(Movie.id == movie_id))
        db.execute(delete(User).where(User.id.in_([customer_a_id, customer_b_id])))


def test_two_customers_cannot_hold_the_same_seat():
    session_factory = make_test_session_factory()
    scenario = seed_booking_scenario(session_factory)

    try:
        show_id, seat_id, customer_a_id, customer_b_id, *_ = scenario
        # Yahan existing Barrier, booking calls aur dono assertions rakho.
        start = Barrier(2)

        def try_booking(user_id):
            with session_factory() as db:
                start.wait(timeout=10)
                try:
                    create_booking(
                        db,
                        user_id=user_id,
                        data=BookingCreate(show_id=show_id, seat_ids=[seat_id])
                    )
                except HTTPException as exc:
                    return exc.status_code
                return 201

        with ThreadPoolExecutor(max_workers=2) as executor:
            attempt_a = executor.submit(try_booking, customer_a_id)
            attempt_b = executor.submit(try_booking, customer_b_id)
            outcomes = [attempt_a.result(), attempt_b.result()]

        assert sorted(outcomes) == [201, 409]

        with session_factory() as db:
            hold_count = db.scalar(
                select(func.count())
                .select_from(BookingSeat)
                .join(Booking, BookingSeat.booking_id == Booking.id)
                .where(
                    Booking.show_id == show_id,
                    BookingSeat.seat_id == seat_id,
                )
            )

        assert hold_count == 1


    finally:
        cleanup_booking_scenario(session_factory, scenario)