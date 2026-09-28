"""In-memory clinic calendar for Maple Street Dental.

Lectures: 5.2 (pure Python first), 5.3-5.6 (booking tools), 11.2 (identity checks).

The scheduler is deliberately framework-free: every rule a voice agent must
respect (opening hours, 30-minute slots, lunch break, booking window, 24-hour
cancellation policy) lives here and is covered by fast unit tests. The agent
tools in ``agents/common.py`` are thin wrappers that turn
:class:`SchedulerError` subclasses into speakable ``ToolError`` messages.

All datetimes are naive and expressed in the clinic's local time zone.
"today" (and optionally "now") are injected so tests are deterministic::

    from datetime import date
    from maple.scheduler import ClinicScheduler

    sched = ClinicScheduler(today=date(2026, 10, 5))
    slots = sched.find_slots("tomorrow", part_of_day="morning")
    appt = sched.book("Ana Gomez", "512-555-0188", slots[0].start, reason="cleaning")
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta
from typing import Literal

PartOfDay = Literal["morning", "afternoon", "any"]
AppointmentStatus = Literal["booked", "cancelled"]

SLOT_MINUTES = 30
CANCELLATION_NOTICE_HOURS = 24


# --------------------------------------------------------------------------------------
# Exceptions: every message is safe to read aloud to a caller.
# --------------------------------------------------------------------------------------


class SchedulerError(Exception):
    """Base class for scheduling problems. ``str(exc)`` is a speakable sentence."""


class InvalidDateError(SchedulerError):
    """The date or time text could not be understood."""


class PastDateError(SchedulerError):
    """The requested date or time is in the past."""


class ClinicClosedError(SchedulerError):
    """The clinic is closed on the requested day or at the requested time."""


class OutsideBookingWindowError(SchedulerError):
    """The requested date is further out than the clinic books."""


class SlotUnavailableError(SchedulerError):
    """The requested slot is already taken or not bookable."""


class InvalidPhoneError(SchedulerError):
    """The phone number is not a valid ten-digit North American number."""


class ValidationError(SchedulerError):
    """A required field such as the patient's name is missing."""


class AppointmentNotFoundError(SchedulerError):
    """No matching appointment exists."""


# --------------------------------------------------------------------------------------
# Data classes
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class OpeningHours:
    """Opening hours for one weekday, with an optional lunch break."""

    open: time
    close: time
    lunch_start: time | None = None
    lunch_end: time | None = None

    def contains(self, start: time, minutes: int = SLOT_MINUTES) -> bool:
        """Return True if a visit starting at ``start`` fits inside these hours."""
        start_dt = datetime.combine(date.min, start)
        end_dt = start_dt + timedelta(minutes=minutes)
        if start < self.open or end_dt.time() > self.close or end_dt.date() != date.min:
            return False
        if self.lunch_start and self.lunch_end:
            lunch_start = datetime.combine(date.min, self.lunch_start)
            lunch_end = datetime.combine(date.min, self.lunch_end)
            if start_dt < lunch_end and end_dt > lunch_start:
                return False
        return True


# Monday=0 ... Sunday=6. ``None`` means closed.
DEFAULT_HOURS: Mapping[int, OpeningHours | None] = {
    0: OpeningHours(time(8, 0), time(17, 0), time(12, 0), time(13, 0)),
    1: OpeningHours(time(8, 0), time(17, 0), time(12, 0), time(13, 0)),
    2: OpeningHours(time(8, 0), time(17, 0), time(12, 0), time(13, 0)),
    3: OpeningHours(time(8, 0), time(17, 0), time(12, 0), time(13, 0)),
    4: OpeningHours(time(8, 0), time(14, 0)),
    5: OpeningHours(time(9, 0), time(13, 0)),
    6: None,
}


@dataclass(frozen=True)
class Slot:
    """A free 30-minute slot."""

    start: datetime

    @property
    def end(self) -> datetime:
        """End time of the slot."""
        return self.start + timedelta(minutes=SLOT_MINUTES)

    @property
    def iso(self) -> str:
        """Machine-friendly start, e.g. ``"2026-10-06T09:30"`` (what tools pass back)."""
        return self.start.strftime("%Y-%m-%dT%H:%M")


@dataclass(frozen=True)
class WaitlistEntry:
    """A caller waiting for an opening on a preferred day."""

    id: str
    patient_name: str
    phone: str
    preferred_day: date
    part_of_day: str = "any"


@dataclass
class Appointment:
    """A booked (or cancelled) appointment."""

    id: str
    patient_name: str
    phone: str
    start: datetime
    reason: str
    status: AppointmentStatus = "booked"
    date_of_birth: date | None = None
    duration_minutes: int = SLOT_MINUTES
    history: list[str] = field(default_factory=list)

    @property
    def iso_start(self) -> str:
        """Start time as ``YYYY-MM-DDTHH:MM``."""
        return self.start.strftime("%Y-%m-%dT%H:%M")

    @property
    def is_active(self) -> bool:
        """True unless the appointment was cancelled."""
        return self.status == "booked"


# --------------------------------------------------------------------------------------
# Parsing helpers
# --------------------------------------------------------------------------------------

_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
_MONTHS = {
    name: i + 1
    for i, names in enumerate(
        [
            ("january", "jan"),
            ("february", "feb"),
            ("march", "mar"),
            ("april", "apr"),
            ("may",),
            ("june", "jun"),
            ("july", "jul"),
            ("august", "aug"),
            ("september", "sep", "sept"),
            ("october", "oct"),
            ("november", "nov"),
            ("december", "dec"),
        ]
    )
    for name in names
}
_ORDINAL_SUFFIX = re.compile(r"(\d+)(st|nd|rd|th)\b")


def normalize_phone(phone: str) -> str:
    """Return a ten-digit phone string, or raise :class:`InvalidPhoneError`.

    Accepts common formats such as ``(512) 555-0142``, ``512.555.0142`` and
    ``+1 512 555 0142``.
    """
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        raise InvalidPhoneError(
            "That phone number doesn't look complete. Could you say the full ten digit number?"
        )
    return digits


def _year_for(month: int, day: int, today: date) -> date:
    candidate = date(today.year, month, day)
    if candidate < today:
        candidate = date(today.year + 1, month, day)
    return candidate


def parse_day(text: str | date, today: date) -> date:
    """Parse a spoken or written day relative to ``today``.

    Supported forms: ``today``, ``tomorrow``, ``day after tomorrow``, weekday
    names (``thursday``, ``this thursday``, ``next thursday``), ISO dates
    (``2026-10-06``), US numeric dates (``10/06`` or ``10/06/2026``) and month
    names (``October 6``, ``Oct 6th``, ``6 October 2026``).

    A bare weekday means the next occurrence strictly after today. ``next
    <weekday>`` means that weekday in the following calendar week.

    Raises:
        InvalidDateError: If the text cannot be parsed.
    """
    if isinstance(text, date) and not isinstance(text, datetime):
        return text
    if isinstance(text, datetime):
        return text.date()

    raw = text.strip().lower().rstrip(".")
    cleaned = _ORDINAL_SUFFIX.sub(r"\1", raw).replace(",", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if cleaned in ("today", "this day"):
        return today
    if cleaned == "tomorrow":
        return today + timedelta(days=1)
    if cleaned in ("day after tomorrow", "the day after tomorrow"):
        return today + timedelta(days=2)

    words = cleaned.split(" ")
    if words and words[-1] in _WEEKDAYS and len(words) <= 2:
        modifier = words[0] if len(words) == 2 else ""
        if modifier not in ("", "this", "next", "on"):
            raise InvalidDateError(f"Sorry, I didn't catch which day you meant by {text!r}.")
        target = _WEEKDAYS.index(words[-1])
        delta = (target - today.weekday()) % 7 or 7
        result = today + timedelta(days=delta)
        if modifier == "next" and result.isocalendar()[1] == today.isocalendar()[1]:
            result += timedelta(days=7)
        return result

    try:
        return date.fromisoformat(cleaned)
    except ValueError:
        pass

    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?", cleaned)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        try:
            if m.group(3):
                year = int(m.group(3))
                year = year + 2000 if year < 100 else year
                return date(year, month, day)
            return _year_for(month, day, today)
        except ValueError as exc:
            raise InvalidDateError(f"Sorry, {text!r} isn't a valid date.") from exc

    m = re.fullmatch(r"(?:[a-z]+ )?([a-z]+) (\d{1,2})(?: (\d{4}))?", cleaned) or re.fullmatch(
        r"(?:[a-z]+ )?(\d{1,2}) ([a-z]+)(?: (\d{4}))?", cleaned
    )
    if m:
        first, second, year_text = m.group(1), m.group(2), m.group(3)
        month_name, day_text = (first, second) if first.isalpha() else (second, first)
        if month_name in _MONTHS:
            try:
                month, day = _MONTHS[month_name], int(day_text)
                if year_text:
                    return date(int(year_text), month, day)
                return _year_for(month, day, today)
            except ValueError as exc:
                raise InvalidDateError(f"Sorry, {text!r} isn't a valid date.") from exc

    raise InvalidDateError(
        f"Sorry, I couldn't understand the date {text!r}. Could you say the day and month?"
    )


def parse_start(text: str | datetime) -> datetime:
    """Parse a slot start such as ``"2026-10-06T09:30"`` or ``"2026-10-06 09:30"``.

    Raises:
        InvalidDateError: If the text is not an ISO date and time.
    """
    if isinstance(text, datetime):
        return text.replace(second=0, microsecond=0)
    try:
        return datetime.fromisoformat(text.strip().replace(" ", "T")).replace(
            second=0, microsecond=0, tzinfo=None
        )
    except ValueError as exc:
        raise InvalidDateError(
            f"Sorry, I couldn't read the time {text!r}. Please pick one of the offered times."
        ) from exc


def parse_date_of_birth(text: str | date) -> date:
    """Parse a date of birth (ISO, ``MM/DD/YYYY`` or ``Month D YYYY``).

    Raises:
        InvalidDateError: If the text is not a full date with a year.
    """
    if isinstance(text, date):
        return text
    raw = _ORDINAL_SUFFIX.sub(r"\1", text.strip().lower()).replace(",", " ")
    raw = re.sub(r"\s+", " ", raw)
    try:
        return date.fromisoformat(raw)
    except ValueError:
        pass
    m = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", raw)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError as exc:
            raise InvalidDateError("That date of birth doesn't look valid.") from exc
    m = re.fullmatch(r"([a-z]+) (\d{1,2}) (\d{4})", raw) or re.fullmatch(r"(\d{1,2}) ([a-z]+) (\d{4})", raw)
    if m:
        a, b, year = m.group(1), m.group(2), int(m.group(3))
        month_name, day_text = (a, b) if a.isalpha() else (b, a)
        if month_name in _MONTHS:
            try:
                return date(year, _MONTHS[month_name], int(day_text))
            except ValueError as exc:
                raise InvalidDateError("That date of birth doesn't look valid.") from exc
    raise InvalidDateError("Please tell me your full date of birth, including the year.")


# --------------------------------------------------------------------------------------
# Scheduler
# --------------------------------------------------------------------------------------


class ClinicScheduler:
    """A deterministic in-memory calendar.

    Args:
        today: The clinic's current date. Defaults to ``date.today()``.
        now: Current clock time on ``today``. Same-day slots before
            ``now + min_notice_minutes`` are hidden. ``None`` means the start of
            the day, so every slot today is still bookable.
        hours: Weekday to :class:`OpeningHours` mapping (``None`` = closed).
        booking_window_days: How far ahead callers may book.
        min_notice_minutes: Minimum notice for a same-day booking.
    """

    def __init__(
        self,
        today: date | None = None,
        *,
        now: time | None = None,
        hours: Mapping[int, OpeningHours | None] | None = None,
        booking_window_days: int = 60,
        min_notice_minutes: int = 60,
    ) -> None:
        self._today = today or date.today()
        self._now = now
        self._hours: Mapping[int, OpeningHours | None] = hours or DEFAULT_HOURS
        self.booking_window_days = booking_window_days
        self.min_notice_minutes = min_notice_minutes
        self._appointments: dict[str, Appointment] = {}
        self._waitlist: list[WaitlistEntry] = []
        self._next_id = 1001

    # -- basic properties ---------------------------------------------------------

    @property
    def today(self) -> date:
        """The injected current date."""
        return self._today

    @property
    def now(self) -> datetime:
        """The injected current datetime (start of day if no time was given)."""
        return datetime.combine(self._today, self._now or time(0, 0))

    @property
    def last_bookable_day(self) -> date:
        """The furthest date callers may book."""
        return self._today + timedelta(days=self.booking_window_days)

    def hours_for(self, day: date) -> OpeningHours | None:
        """Return opening hours for ``day`` or ``None`` when closed."""
        return self._hours.get(day.weekday())

    def is_open(self, day: date) -> bool:
        """True if the clinic has opening hours on ``day``."""
        return self.hours_for(day) is not None

    # -- availability ---------------------------------------------------------------

    def _all_slot_starts(self, day: date) -> list[datetime]:
        hours = self.hours_for(day)
        if hours is None:
            return []
        starts: list[datetime] = []
        cursor = datetime.combine(day, hours.open)
        closing = datetime.combine(day, hours.close)
        while cursor + timedelta(minutes=SLOT_MINUTES) <= closing:
            if hours.contains(cursor.time()):
                starts.append(cursor)
            cursor += timedelta(minutes=SLOT_MINUTES)
        return starts

    def _booked_starts(self, exclude_id: str | None = None) -> set[datetime]:
        return {a.start for a in self._appointments.values() if a.is_active and a.id != exclude_id}

    def _validate_day(self, day: date) -> None:
        if day < self._today:
            raise PastDateError("That date has already passed. Which upcoming day works for you?")
        if day > self.last_bookable_day:
            raise OutsideBookingWindowError(
                f"We only book up to {self.booking_window_days} days ahead. Could you pick an earlier date?"
            )
        if not self.is_open(day):
            raise ClinicClosedError(f"We're closed on {day.strftime('%A')}s. Would another day work?")

    def _earliest_bookable(self) -> datetime:
        return self.now + timedelta(minutes=self.min_notice_minutes) if self._now else self.now

    def find_slots(
        self,
        day: date | str,
        part_of_day: PartOfDay | str = "any",
        limit: int | None = None,
        *,
        exclude_appointment_id: str | None = None,
    ) -> list[Slot]:
        """Return free slots on ``day``, earliest first.

        Args:
            day: A :class:`date` or text understood by :func:`parse_day`.
            part_of_day: ``"morning"`` (before noon), ``"afternoon"`` (noon or
                later) or ``"any"``.
            limit: Maximum number of slots to return.
            exclude_appointment_id: Treat this appointment's slot as free
                (useful when rescheduling).

        Raises:
            InvalidDateError, PastDateError, OutsideBookingWindowError,
            ClinicClosedError: When the day cannot be booked.
        """
        target = parse_day(day, self._today)
        self._validate_day(target)
        part = (part_of_day or "any").lower()
        if part not in ("morning", "afternoon", "any"):
            raise ValidationError("Would you prefer the morning or the afternoon?")

        taken = self._booked_starts(exclude_id=exclude_appointment_id)
        earliest = self._earliest_bookable()
        slots: list[Slot] = []
        for start in self._all_slot_starts(target):
            if start in taken or start < earliest:
                continue
            if part == "morning" and start.hour >= 12:
                continue
            if part == "afternoon" and start.hour < 12:
                continue
            slots.append(Slot(start))
            if limit is not None and len(slots) >= limit:
                break
        return slots

    def next_available(
        self,
        start_day: date | str | None = None,
        part_of_day: PartOfDay | str = "any",
        limit: int = 3,
        search_days: int = 14,
    ) -> list[Slot]:
        """Return up to ``limit`` slots on the first day (from ``start_day``) that has any.

        Closed days are skipped silently. Returns an empty list when nothing is
        free within ``search_days`` or the booking window.
        """
        day = parse_day(start_day, self._today) if start_day is not None else self._today
        day = max(day, self._today)
        for offset in range(search_days + 1):
            candidate = day + timedelta(days=offset)
            if candidate > self.last_bookable_day:
                break
            if not self.is_open(candidate):
                continue
            slots = self.find_slots(candidate, part_of_day, limit)
            if slots:
                return slots
        return []

    def is_available(self, start: datetime | str, *, exclude_appointment_id: str | None = None) -> bool:
        """True if ``start`` is a valid, free slot start."""
        try:
            self._check_bookable(parse_start(start), exclude_appointment_id)
        except SchedulerError:
            return False
        return True

    def _check_bookable(self, start: datetime, exclude_id: str | None = None) -> None:
        self._validate_day(start.date())
        if start not in self._all_slot_starts(start.date()):
            raise ClinicClosedError(
                "That time is outside our appointment hours. Let me find you an open time."
            )
        if start < self._earliest_bookable():
            raise PastDateError("That time is too soon to book. Would a later time work?")
        if start in self._booked_starts(exclude_id=exclude_id):
            raise SlotUnavailableError(
                "Sorry, that time was just taken. Would you like to hear the next available times?"
            )

    # -- mutations ------------------------------------------------------------------

    def book(
        self,
        patient_name: str,
        phone: str,
        start: datetime | str,
        reason: str = "checkup",
        date_of_birth: date | str | None = None,
    ) -> Appointment:
        """Book a new appointment.

        Raises:
            ValidationError: If the name is missing.
            InvalidPhoneError: If the phone number is not ten digits.
            SchedulerError subclasses: If the slot cannot be booked.
        """
        name = " ".join(patient_name.split())
        if len(name) < 2:
            raise ValidationError("Could I get the patient's full name, please?")
        digits = normalize_phone(phone)
        when = parse_start(start)
        self._check_bookable(when)
        dob = parse_date_of_birth(date_of_birth) if date_of_birth else None
        appt = Appointment(
            id=f"APT-{self._next_id}",
            patient_name=name,
            phone=digits,
            start=when,
            reason=(reason or "checkup").strip(),
            date_of_birth=dob,
        )
        appt.history.append(f"booked {appt.iso_start}")
        self._next_id += 1
        self._appointments[appt.id] = appt
        return replace(appt, history=list(appt.history))

    def get(self, appointment_id: str) -> Appointment:
        """Return a copy of an appointment by ID.

        Raises:
            AppointmentNotFoundError: If the ID is unknown.
        """
        appt = self._appointments.get(appointment_id.strip().upper())
        if appt is None:
            raise AppointmentNotFoundError("I couldn't find that appointment.")
        return replace(appt, history=list(appt.history))

    def reschedule(self, appointment_id: str, new_start: datetime | str) -> Appointment:
        """Move an active appointment to a new free slot.

        Raises:
            AppointmentNotFoundError: If the appointment is unknown or cancelled.
            SchedulerError subclasses: If the new slot cannot be booked.
        """
        appt = self._appointments.get(appointment_id.strip().upper())
        if appt is None or not appt.is_active:
            raise AppointmentNotFoundError("I couldn't find an active appointment to move.")
        when = parse_start(new_start)
        if when == appt.start:
            raise SlotUnavailableError("That's already the time of your appointment.")
        self._check_bookable(when, exclude_id=appt.id)
        appt.history.append(f"rescheduled {appt.iso_start} -> {when.strftime('%Y-%m-%dT%H:%M')}")
        appt.start = when
        return replace(appt, history=list(appt.history))

    def cancel(self, appointment_id: str) -> Appointment:
        """Cancel an active appointment and free its slot.

        Raises:
            AppointmentNotFoundError: If the appointment is unknown or already cancelled.
        """
        appt = self._appointments.get(appointment_id.strip().upper())
        if appt is None or not appt.is_active:
            raise AppointmentNotFoundError("I couldn't find an active appointment to cancel.")
        appt.status = "cancelled"
        appt.history.append("cancelled")
        return replace(appt, history=list(appt.history))

    # -- waitlist (lecture 5.9 challenge) ---------------------------------------------

    def add_to_waitlist(
        self,
        patient_name: str,
        phone: str,
        preferred_day: date | str,
        part_of_day: PartOfDay | str = "any",
    ) -> WaitlistEntry:
        """Add a caller to the waitlist for ``preferred_day``.

        The same phone number can only wait once per day; a second request for
        the same day returns the existing entry instead of duplicating it.

        Raises:
            ValidationError: If the name is missing or ``part_of_day`` is invalid.
            InvalidPhoneError: If the phone number is not ten digits.
            InvalidDateError, PastDateError, OutsideBookingWindowError,
            ClinicClosedError: If the day cannot be booked at all.
        """
        name = " ".join(patient_name.split())
        if len(name) < 2:
            raise ValidationError("Could I get the patient's full name for the waitlist?")
        digits = normalize_phone(phone)
        day = parse_day(preferred_day, self._today)
        self._validate_day(day)
        part = (part_of_day or "any").lower()
        if part not in ("morning", "afternoon", "any"):
            raise ValidationError("Would you prefer the morning or the afternoon?")
        for entry in self._waitlist:
            if entry.phone == digits and entry.preferred_day == day:
                return entry
        entry = WaitlistEntry(
            id=f"WL-{len(self._waitlist) + 1:03d}",
            patient_name=name,
            phone=digits,
            preferred_day=day,
            part_of_day=part,
        )
        self._waitlist.append(entry)
        return entry

    def waitlist(self, day: date | str | None = None) -> list[WaitlistEntry]:
        """Return waitlist entries in the order they joined, optionally for one day."""
        if day is None:
            return list(self._waitlist)
        target = parse_day(day, self._today)
        return [e for e in self._waitlist if e.preferred_day == target]

    def waitlist_position(self, entry_id: str) -> int:
        """1-based position of an entry among callers waiting for the same day.

        Raises:
            AppointmentNotFoundError: If the entry does not exist.
        """
        entry = next((e for e in self._waitlist if e.id == entry_id), None)
        if entry is None:
            raise AppointmentNotFoundError("I couldn't find that waitlist entry.")
        same_day = [e for e in self._waitlist if e.preferred_day == entry.preferred_day]
        return same_day.index(entry) + 1

    # -- lookups ----------------------------------------------------------------------

    def find_by_phone(self, phone: str, *, include_cancelled: bool = False) -> list[Appointment]:
        """Return appointments for a phone number, earliest first."""
        digits = normalize_phone(phone)
        matches = [
            replace(a, history=list(a.history))
            for a in self._appointments.values()
            if a.phone == digits and (include_cancelled or a.is_active)
        ]
        return sorted(matches, key=lambda a: a.start)

    def upcoming_for_phone(self, phone: str) -> Appointment | None:
        """Return the caller's next active appointment from today on, if any."""
        for appt in self.find_by_phone(phone):
            if appt.start.date() >= self._today:
                return appt
        return None

    def verify_patient(self, phone: str, date_of_birth: date | str) -> bool:
        """True if an appointment on file matches both the phone and date of birth."""
        try:
            digits = normalize_phone(phone)
            dob = parse_date_of_birth(date_of_birth)
        except SchedulerError:
            return False
        return any(a.phone == digits and a.date_of_birth == dob for a in self._appointments.values())

    def is_late_cancellation(self, appointment: Appointment) -> bool:
        """True if cancelling now gives less than 24 hours' notice."""
        return appointment.start - self.now < timedelta(hours=CANCELLATION_NOTICE_HOURS)

    def all_appointments(self) -> list[Appointment]:
        """Return copies of every appointment (active and cancelled), earliest first."""
        return sorted(
            (replace(a, history=list(a.history)) for a in self._appointments.values()),
            key=lambda a: a.start,
        )

    # -- demo data --------------------------------------------------------------------

    @classmethod
    def with_demo_data(cls, today: date | None = None, **kwargs: object) -> ClinicScheduler:
        """Return a scheduler pre-loaded with three fictional patients.

        ========================  ===============  ==========
        Patient                   Phone            DOB
        ========================  ===============  ==========
        Jordan Lee                (512) 555-0142   1988-04-12
        Priya Patel               (512) 555-0177   1990-11-02
        Sam Rivera                (512) 555-0123   1975-07-30
        ========================  ===============  ==========

        Appointments land on the first, second and third open days after
        ``today`` so the data is always in the future.
        """
        sched = cls(today, **kwargs)  # type: ignore[arg-type]
        open_days: list[date] = []
        cursor = sched.today + timedelta(days=1)
        while len(open_days) < 3:
            if sched.is_open(cursor):
                open_days.append(cursor)
            cursor += timedelta(days=1)
        demo = [
            ("Jordan Lee", "5125550142", time(10, 0), "cleaning", date(1988, 4, 12)),
            ("Priya Patel", "5125550177", time(9, 0), "filling", date(1990, 11, 2)),
            ("Sam Rivera", "5125550123", time(11, 0), "checkup", date(1975, 7, 30)),
        ]
        for day, (name, phone, at, reason, dob) in zip(open_days, demo, strict=True):
            sched.book(name, phone, datetime.combine(day, at), reason, dob)
        return sched
