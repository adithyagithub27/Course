"""Unit tests for maple.scheduler (lectures 5.2, 5.9, 11.2)."""

from __future__ import annotations

from datetime import date, datetime, time

import pytest

from maple.scheduler import (
    AppointmentNotFoundError,
    ClinicClosedError,
    ClinicScheduler,
    InvalidDateError,
    InvalidPhoneError,
    OutsideBookingWindowError,
    PastDateError,
    SchedulerError,
    SlotUnavailableError,
    ValidationError,
    normalize_phone,
    parse_date_of_birth,
    parse_day,
    parse_start,
)

MONDAY = date(2026, 10, 5)  # a Monday


@pytest.fixture
def sched() -> ClinicScheduler:
    return ClinicScheduler(today=MONDAY)


# -- parsing ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("today", date(2026, 10, 5)),
        ("tomorrow", date(2026, 10, 6)),
        ("day after tomorrow", date(2026, 10, 7)),
        ("Thursday", date(2026, 10, 8)),
        ("this friday", date(2026, 10, 9)),
        ("monday", date(2026, 10, 12)),  # bare weekday = next occurrence after today
        ("next wednesday", date(2026, 10, 14)),  # following calendar week
        ("2026-10-20", date(2026, 10, 20)),
        ("10/21", date(2026, 10, 21)),
        ("10/21/2026", date(2026, 10, 21)),
        ("October 22nd", date(2026, 10, 22)),
        ("Oct 23", date(2026, 10, 23)),
        ("23 October 2026", date(2026, 10, 23)),
        ("January 5", date(2027, 1, 5)),  # past month rolls to next year
    ],
)
def test_parse_day(text: str, expected: date) -> None:
    assert parse_day(text, MONDAY) == expected


def test_parse_day_accepts_date_objects() -> None:
    assert parse_day(date(2026, 11, 1), MONDAY) == date(2026, 11, 1)
    assert parse_day(datetime(2026, 11, 1, 9, 30), MONDAY) == date(2026, 11, 1)


@pytest.mark.parametrize("text", ["someday", "the 45th", "13/45", "February 30", "next blursday"])
def test_parse_day_rejects_garbage(text: str) -> None:
    with pytest.raises(InvalidDateError):
        parse_day(text, MONDAY)


def test_parse_start_formats() -> None:
    assert parse_start("2026-10-06T09:30") == datetime(2026, 10, 6, 9, 30)
    assert parse_start("2026-10-06 09:30") == datetime(2026, 10, 6, 9, 30)
    with pytest.raises(InvalidDateError):
        parse_start("half past nine")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1988-04-12", date(1988, 4, 12)),
        ("04/12/1988", date(1988, 4, 12)),
        ("April 12th, 1988", date(1988, 4, 12)),
    ],
)
def test_parse_date_of_birth(text: str, expected: date) -> None:
    assert parse_date_of_birth(text) == expected


def test_parse_date_of_birth_requires_year() -> None:
    with pytest.raises(InvalidDateError):
        parse_date_of_birth("April 12")


@pytest.mark.parametrize(
    "raw", ["(512) 555-0142", "512-555-0142", "512.555.0142", "+1 512 555 0142", "15125550142"]
)
def test_normalize_phone(raw: str) -> None:
    assert normalize_phone(raw) == "5125550142"


def test_normalize_phone_rejects_short_numbers() -> None:
    with pytest.raises(InvalidPhoneError):
        normalize_phone("555-0142")


# -- availability ----------------------------------------------------------------------


def test_weekday_has_fourteen_slots_with_lunch_gap(sched: ClinicScheduler) -> None:
    slots = sched.find_slots("tomorrow")
    starts = [s.start.time() for s in slots]
    assert len(slots) == 16  # 8:00-12:00 (8) + 13:00-17:00 (8)
    assert time(12, 0) not in starts and time(12, 30) not in starts
    assert starts[0] == time(8, 0) and starts[-1] == time(16, 30)


def test_friday_and_saturday_hours(sched: ClinicScheduler) -> None:
    friday = sched.find_slots("friday")
    saturday = sched.find_slots("saturday")
    assert friday[-1].start.time() == time(13, 30)
    assert saturday[0].start.time() == time(9, 0) and saturday[-1].start.time() == time(12, 30)


def test_part_of_day_filter(sched: ClinicScheduler) -> None:
    morning = sched.find_slots("tomorrow", "morning")
    afternoon = sched.find_slots("tomorrow", "afternoon")
    assert all(s.start.hour < 12 for s in morning)
    assert all(s.start.hour >= 12 for s in afternoon)
    assert len(morning) + len(afternoon) == len(sched.find_slots("tomorrow"))


def test_limit(sched: ClinicScheduler) -> None:
    assert len(sched.find_slots("tomorrow", limit=3)) == 3


def test_invalid_part_of_day(sched: ClinicScheduler) -> None:
    with pytest.raises(ValidationError):
        sched.find_slots("tomorrow", "evening")


def test_closed_on_sunday(sched: ClinicScheduler) -> None:
    with pytest.raises(ClinicClosedError):
        sched.find_slots("sunday")


def test_past_date_rejected(sched: ClinicScheduler) -> None:
    with pytest.raises(PastDateError):
        sched.find_slots(date(2026, 10, 1))


def test_booking_window(sched: ClinicScheduler) -> None:
    with pytest.raises(OutsideBookingWindowError):
        sched.find_slots(date(2027, 3, 1))


def test_same_day_min_notice() -> None:
    sched = ClinicScheduler(today=MONDAY, now=time(10, 10), min_notice_minutes=60)
    first = sched.find_slots("today")[0]
    assert first.start.time() == time(11, 30)


def test_booked_slot_disappears(sched: ClinicScheduler) -> None:
    slot = sched.find_slots("tomorrow")[0]
    sched.book("Ana Gomez", "512-555-0188", slot.start, "cleaning")
    assert slot not in sched.find_slots("tomorrow")
    assert not sched.is_available(slot.start)


def test_next_available_skips_closed_and_full_days(sched: ClinicScheduler) -> None:
    saturday = date(2026, 10, 10)
    for slot in sched.find_slots(saturday):
        sched.book("Filler Patient", "512-555-0100", slot.start, "checkup")
    result = sched.next_available(saturday, limit=2)
    assert result[0].start.date() == date(2026, 10, 12)  # Sat full, Sun closed -> Monday
    assert len(result) == 2


def test_slot_iso_and_end(sched: ClinicScheduler) -> None:
    slot = sched.find_slots("tomorrow")[0]
    assert slot.iso == "2026-10-06T08:00"
    assert (slot.end - slot.start).total_seconds() == 1800


# -- booking, reschedule, cancel -------------------------------------------------------


def test_book_returns_copy_with_normalized_fields(sched: ClinicScheduler) -> None:
    appt = sched.book("  Ana   Gomez ", "(512) 555-0188", "2026-10-06T09:30", "cleaning")
    assert appt.id == "APT-1001"
    assert appt.patient_name == "Ana Gomez"
    assert appt.phone == "5125550188"
    assert appt.is_active and appt.iso_start == "2026-10-06T09:30"
    appt.patient_name = "Changed"  # mutating the copy must not change the calendar
    assert sched.get("APT-1001").patient_name == "Ana Gomez"


def test_double_booking_raises(sched: ClinicScheduler) -> None:
    sched.book("Ana Gomez", "512-555-0188", "2026-10-06T09:30", "cleaning")
    with pytest.raises(SlotUnavailableError):
        sched.book("Ben Ortiz", "512-555-0199", "2026-10-06T09:30", "checkup")


@pytest.mark.parametrize(
    "start", ["2026-10-06T12:00", "2026-10-06T07:30", "2026-10-06T09:15", "2026-10-06T17:00"]
)
def test_book_outside_hours_raises(sched: ClinicScheduler, start: str) -> None:
    with pytest.raises(ClinicClosedError):
        sched.book("Ana Gomez", "512-555-0188", start, "cleaning")


def test_book_requires_name_and_valid_phone(sched: ClinicScheduler) -> None:
    with pytest.raises(ValidationError):
        sched.book(" ", "512-555-0188", "2026-10-06T09:30")
    with pytest.raises(InvalidPhoneError):
        sched.book("Ana Gomez", "555", "2026-10-06T09:30")


def test_reschedule_frees_old_slot(sched: ClinicScheduler) -> None:
    appt = sched.book("Ana Gomez", "512-555-0188", "2026-10-06T09:30", "cleaning")
    moved = sched.reschedule(appt.id, "2026-10-07T14:00")
    assert moved.start == datetime(2026, 10, 7, 14, 0)
    assert sched.is_available("2026-10-06T09:30")
    assert "rescheduled" in moved.history[-1]


def test_reschedule_to_same_time_or_taken_slot(sched: ClinicScheduler) -> None:
    a = sched.book("Ana Gomez", "512-555-0188", "2026-10-06T09:30", "cleaning")
    sched.book("Ben Ortiz", "512-555-0199", "2026-10-06T10:00", "checkup")
    with pytest.raises(SlotUnavailableError):
        sched.reschedule(a.id, "2026-10-06T09:30")
    with pytest.raises(SlotUnavailableError):
        sched.reschedule(a.id, "2026-10-06T10:00")


def test_cancel_frees_slot_and_blocks_second_cancel(sched: ClinicScheduler) -> None:
    appt = sched.book("Ana Gomez", "512-555-0188", "2026-10-06T09:30", "cleaning")
    cancelled = sched.cancel(appt.id)
    assert cancelled.status == "cancelled"
    assert sched.is_available("2026-10-06T09:30")
    with pytest.raises(AppointmentNotFoundError):
        sched.cancel(appt.id)
    with pytest.raises(AppointmentNotFoundError):
        sched.reschedule(appt.id, "2026-10-07T09:00")


def test_unknown_appointment(sched: ClinicScheduler) -> None:
    with pytest.raises(AppointmentNotFoundError):
        sched.get("APT-9999")


def test_late_cancellation_policy() -> None:
    sched = ClinicScheduler(today=MONDAY, now=time(9, 0), min_notice_minutes=0)
    soon = sched.book("Ana Gomez", "512-555-0188", "2026-10-06T08:30", "cleaning")
    later = sched.book("Ben Ortiz", "512-555-0199", "2026-10-07T09:30", "checkup")
    assert sched.is_late_cancellation(soon) is True
    assert sched.is_late_cancellation(later) is False


def test_all_errors_are_scheduler_errors_with_speakable_text(sched: ClinicScheduler) -> None:
    with pytest.raises(SchedulerError) as info:
        sched.find_slots("sunday")
    message = str(info.value)
    assert message.endswith("?") or message.endswith(".")
    assert "Error" not in message


# -- lookups and verification ----------------------------------------------------------


def test_demo_data_is_in_the_future_and_verifiable() -> None:
    sched = ClinicScheduler.with_demo_data(MONDAY)
    appts = sched.all_appointments()
    assert [a.patient_name for a in appts] == ["Jordan Lee", "Priya Patel", "Sam Rivera"]
    assert all(a.start.date() > MONDAY for a in appts)
    assert sched.verify_patient("(512) 555-0142", "1988-04-12")
    assert not sched.verify_patient("(512) 555-0142", "1990-01-01")
    assert not sched.verify_patient("not a phone", "1988-04-12")


def test_find_by_phone_and_upcoming(sched: ClinicScheduler) -> None:
    sched.book("Ana Gomez", "512-555-0188", "2026-10-08T09:30", "cleaning")
    first = sched.book("Ana Gomez", "512-555-0188", "2026-10-06T09:30", "checkup")
    assert [a.start.day for a in sched.find_by_phone("5125550188")] == [6, 8]
    assert sched.upcoming_for_phone("512 555 0188").id == first.id
    sched.cancel(first.id)
    assert len(sched.find_by_phone("5125550188")) == 1
    assert len(sched.find_by_phone("5125550188", include_cancelled=True)) == 2
    assert sched.upcoming_for_phone("512-555-0000") is None


# -- waitlist (lecture 5.9) ------------------------------------------------------------


def test_add_to_waitlist(sched: ClinicScheduler) -> None:
    entry = sched.add_to_waitlist("Ana Gomez", "512-555-0188", "thursday", "morning")
    assert entry.id == "WL-001"
    assert entry.preferred_day == date(2026, 10, 8)
    assert entry.phone == "5125550188"
    assert sched.waitlist() == [entry]
    assert sched.waitlist("thursday") == [entry]
    assert sched.waitlist("friday") == []


def test_waitlist_is_deduplicated_per_phone_and_day(sched: ClinicScheduler) -> None:
    first = sched.add_to_waitlist("Ana Gomez", "512-555-0188", "thursday")
    again = sched.add_to_waitlist("Ana Gomez", "(512) 555-0188", "2026-10-08")
    assert again == first
    assert len(sched.waitlist()) == 1


def test_waitlist_position(sched: ClinicScheduler) -> None:
    sched.add_to_waitlist("Ana Gomez", "512-555-0188", "thursday")
    other_day = sched.add_to_waitlist("Cy Young", "512-555-0177", "friday")
    second = sched.add_to_waitlist("Ben Ortiz", "512-555-0199", "thursday")
    assert sched.waitlist_position(second.id) == 2
    assert sched.waitlist_position(other_day.id) == 1
    with pytest.raises(AppointmentNotFoundError):
        sched.waitlist_position("WL-999")


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"patient_name": "", "phone": "512-555-0188", "preferred_day": "thursday"}, ValidationError),
        ({"patient_name": "Ana", "phone": "0188", "preferred_day": "thursday"}, InvalidPhoneError),
        ({"patient_name": "Ana", "phone": "512-555-0188", "preferred_day": "sunday"}, ClinicClosedError),
        ({"patient_name": "Ana", "phone": "512-555-0188", "preferred_day": "2026-09-01"}, PastDateError),
        ({"patient_name": "Ana", "phone": "512-555-0188", "preferred_day": "someday"}, InvalidDateError),
        (
            {
                "patient_name": "Ana",
                "phone": "512-555-0188",
                "preferred_day": "thursday",
                "part_of_day": "night",
            },
            ValidationError,
        ),
    ],
)
def test_waitlist_validation(sched: ClinicScheduler, kwargs: dict[str, str], error: type[Exception]) -> None:
    with pytest.raises(error):
        sched.add_to_waitlist(**kwargs)
