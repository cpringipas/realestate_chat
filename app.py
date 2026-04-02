import json
import os
import re
import time
import urllib.error
import urllib.request
from copy import deepcopy
from datetime import datetime, timedelta

import streamlit as st


st.set_page_config(
    page_title="M.Residence AI Concierge",
    page_icon="MR",
    layout="wide",
)


LISTINGS = [
    {
        "id": 1,
        "title": "2 bedroom apartment in Strovolos",
        "type": "Apartment",
        "location": "Strovolos",
        "bedrooms": 2,
        "price": 250000,
        "price_label": "EUR250,000",
        "blurb": "Bright modern apartment close to schools, cafes, and central Nicosia access.",
        "tags": ["Balcony", "Parking", "Ideal for first-time buyers"],
    },
    {
        "id": 2,
        "title": "3 bedroom house in Lakatamia",
        "type": "House",
        "location": "Lakatamia",
        "bedrooms": 3,
        "price": 380000,
        "price_label": "EUR380,000",
        "blurb": "Family-ready home with a private garden, covered parking, and quiet residential feel.",
        "tags": ["Garden", "Family area", "Move-in ready"],
    },
    {
        "id": 3,
        "title": "Luxury villa in Limassol",
        "type": "Villa",
        "location": "Limassol",
        "bedrooms": 4,
        "price": 1200000,
        "price_label": "EUR1.2M",
        "blurb": "Premium sea-view villa with pool, designer interiors, and strong prestige appeal.",
        "tags": ["Sea view", "Pool", "Luxury"],
    },
    {
        "id": 4,
        "title": "2 bedroom penthouse in Engomi",
        "type": "Penthouse",
        "location": "Engomi",
        "bedrooms": 2,
        "price": 315000,
        "price_label": "EUR315,000",
        "blurb": "Stylish penthouse with a large veranda and excellent rental potential near embassies.",
        "tags": ["Penthouse", "Veranda", "Investment"],
    },
    {
        "id": 5,
        "title": "3 bedroom apartment in Aglantzia",
        "type": "Apartment",
        "location": "Aglantzia",
        "bedrooms": 3,
        "price": 295000,
        "price_label": "EUR295,000",
        "blurb": "Spacious city apartment well suited to growing families wanting quick Nicosia access.",
        "tags": ["City access", "Large living area", "Near parks"],
    },
    {
        "id": 6,
        "title": "4 bedroom detached home in Archangelos",
        "type": "House",
        "location": "Archangelos",
        "bedrooms": 4,
        "price": 465000,
        "price_label": "EUR465,000",
        "blurb": "Detached home with generous indoor space and a refined suburban neighborhood profile.",
        "tags": ["Detached", "Quiet area", "Parking"],
    },
    {
        "id": 7,
        "title": "1 bedroom apartment in City Center Nicosia",
        "type": "Apartment",
        "location": "Nicosia",
        "bedrooms": 1,
        "price": 185000,
        "price_label": "EUR185,000",
        "blurb": "Compact modern apartment aimed at professionals and investors who want strong city convenience.",
        "tags": ["City center", "Investment", "Modern finish"],
    },
    {
        "id": 8,
        "title": "3 bedroom maisonette in Dasoupoli",
        "type": "Maisonette",
        "location": "Dasoupoli",
        "bedrooms": 3,
        "price": 340000,
        "price_label": "EUR340,000",
        "blurb": "Smartly renovated maisonette with practical family layout and quick access to business districts.",
        "tags": ["Renovated", "Family layout", "Central access"],
    },
    {
        "id": 9,
        "title": "2 bedroom seafront apartment in Limassol",
        "type": "Apartment",
        "location": "Limassol",
        "bedrooms": 2,
        "price": 540000,
        "price_label": "EUR540,000",
        "blurb": "Seafront apartment with premium finishes and strong appeal for lifestyle buyers or holiday use.",
        "tags": ["Seafront", "Premium", "Holiday home"],
    },
    {
        "id": 10,
        "title": "5 bedroom villa in Germasogeia",
        "type": "Villa",
        "location": "Germasogeia",
        "bedrooms": 5,
        "price": 1450000,
        "price_label": "EUR1.45M",
        "blurb": "High-end hillside villa with expansive terraces, private pool, and elevated Limassol views.",
        "tags": ["Hillside", "Private pool", "Prestige"],
    },
]

VIEWING_SLOTS = [
    "Tuesday 11:00",
    "Tuesday 16:30",
    "Wednesday 12:15",
    "Thursday 10:00",
    "Friday 15:45",
]

WEEKDAY_INDEX = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

INITIAL_PROFILE = {
    "name": None,
    "phone": None,
    "budget": None,
    "location": None,
    "timeline": None,
    "bedrooms": None,
    "purpose": None,
    "intent": None,
    "selected_listing": None,
    "viewing_booked": None,
}

RECOMMENDATION_INTROS = [
    "Here are the closest matches I would suggest based on what you have shared:",
    "These are the strongest options I would shortlist for you right now:",
    "From the current brief, these listings look the most relevant:",
]

PROPERTY_INTROS = [
    "Based on your brief, these are the properties I would put forward first:",
    "From what you have told me, I would start with these homes:",
    "At this stage, these look like the best-fit properties to review first:",
]

FALLBACK_INTROS = [
    "I can help with search, comparisons, or a viewing arrangement.",
    "I can narrow this down quickly and keep it practical.",
    "I can help you move from browsing to a realistic shortlist.",
]

QUALIFYING_INTROS = [
    "I can narrow this down properly for you.",
    "Let me tighten the search before I suggest specific homes.",
    "I want to make the shortlist feel relevant, not random.",
]

WELCOME_MESSAGE = (
    "Welcome to **M.Residence**. I can help you explore homes in Cyprus, narrow down the right fit, "
    "and line up a viewing.\n\n"
    "To get started, are you mainly looking for an apartment, house, or villa, and which area is top of mind?"
)


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": WELCOME_MESSAGE, "time": current_time_label()}
        ]
    if "lead_profile" not in st.session_state:
        st.session_state.lead_profile = deepcopy(INITIAL_PROFILE)
    if "shown_listing_ids" not in st.session_state:
        st.session_state.shown_listing_ids = []
    if "response_counters" not in st.session_state:
        st.session_state.response_counters = {"recommend": 0, "property": 0, "fallback": 0}
    if "asked_fields" not in st.session_state:
        st.session_state.asked_fields = []
    if "pending_reply" not in st.session_state:
        st.session_state.pending_reply = None
    if "webhook_status" not in st.session_state:
        st.session_state.webhook_status = "Not sent"
    if "last_sent_fingerprint" not in st.session_state:
        st.session_state.last_sent_fingerprint = None
    if "notification_status" not in st.session_state:
        st.session_state.notification_status = "Not sent"
    if "last_notification_fingerprint" not in st.session_state:
        st.session_state.last_notification_fingerprint = None
    if "follow_up_status" not in st.session_state:
        st.session_state.follow_up_status = "Not sent"
    if "last_follow_up_fingerprint" not in st.session_state:
        st.session_state.last_follow_up_fingerprint = None


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(201, 127, 53, 0.20), transparent 28%),
                radial-gradient(circle at bottom right, rgba(143, 84, 33, 0.18), transparent 22%),
                linear-gradient(135deg, #efe6db 0%, #f8f4ee 48%, #eee2d3 100%);
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1320px;
        }
        .panel {
            background: rgba(255, 250, 244, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.45);
            border-radius: 28px;
            padding: 24px;
            box-shadow: 0 24px 60px rgba(74, 50, 24, 0.16);
            backdrop-filter: blur(18px);
        }
        .eyebrow {
            margin: 0 0 12px 0;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.72rem;
            font-weight: 800;
            color: #8f5421;
        }
        .hero-title {
            margin: 0;
            font-size: clamp(2.2rem, 4vw, 4.4rem);
            line-height: 0.95;
            color: #1f2933;
        }
        .hero-copy {
            margin-top: 18px;
            color: #6c737f;
            line-height: 1.7;
            font-size: 1rem;
        }
        .listing-card {
            background: #fffaf4;
            border: 1px solid rgba(31, 41, 51, 0.12);
            border-radius: 22px;
            padding: 18px;
            margin-top: 14px;
        }
        .listing-title {
            font-weight: 800;
            color: #1f2933;
        }
        .listing-price {
            color: #8f5421;
            font-weight: 800;
        }
        .listing-meta, .listing-blurb, .profile-copy {
            color: #6c737f;
            line-height: 1.6;
        }
        .tag {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: #efd7bf;
            color: #8f5421;
            font-size: 0.78rem;
            font-weight: 700;
            margin: 10px 8px 0 0;
        }
        .section-title {
            margin: 0 0 8px 0;
            color: #1f2933;
        }
        .quick-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        .profile-card {
            background: rgba(255,255,255,0.7);
            border: 1px solid rgba(31, 41, 51, 0.1);
            border-radius: 20px;
            padding: 16px;
            margin-top: 12px;
        }
        .slot {
            display: inline-block;
            padding: 7px 10px;
            border-radius: 999px;
            background: rgba(201, 127, 53, 0.12);
            color: #8f5421;
            border: 1px solid rgba(201, 127, 53, 0.18);
            font-size: 0.83rem;
            font-weight: 700;
            margin: 8px 8px 0 0;
        }
        .wa-shell {
            background: #efeae2;
            border: 1px solid rgba(31, 41, 51, 0.08);
            border-radius: 24px;
            overflow: hidden;
        }
        .wa-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 16px;
            background: #f0f2f5;
            border-bottom: 1px solid rgba(31, 41, 51, 0.08);
        }
        .wa-agent {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .wa-avatar {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: linear-gradient(135deg, #c97f35, #8f5421);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.95rem;
            font-weight: 800;
        }
        .wa-name {
            font-weight: 800;
            color: #111b21;
        }
        .wa-status {
            font-size: 0.84rem;
            color: #667781;
        }
        .wa-thread {
            padding: 18px 16px;
            background:
                radial-gradient(circle at top left, rgba(255,255,255,0.28), transparent 18%),
                linear-gradient(rgba(255,255,255,0.18), rgba(255,255,255,0.18)),
                #e5ddd5;
            min-height: 520px;
        }
        .wa-row {
            display: flex;
            margin-bottom: 12px;
        }
        .wa-row.user {
            justify-content: flex-end;
        }
        .wa-row.assistant {
            justify-content: flex-start;
        }
        .wa-bubble {
            max-width: 78%;
            padding: 10px 12px 18px;
            border-radius: 12px;
            position: relative;
            line-height: 1.5;
            font-size: 0.95rem;
            box-shadow: 0 1px 1px rgba(17, 27, 33, 0.08);
            white-space: pre-wrap;
        }
        .wa-row.assistant .wa-bubble {
            background: white;
            color: #111b21;
            border-top-left-radius: 4px;
        }
        .wa-row.user .wa-bubble {
            background: #d9fdd3;
            color: #111b21;
            border-top-right-radius: 4px;
        }
        .wa-time {
            position: absolute;
            right: 10px;
            bottom: 5px;
            font-size: 0.72rem;
            color: #667781;
        }
        .wa-typing {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 10px 12px;
            border-radius: 12px;
            background: white;
            color: #667781;
            font-size: 0.9rem;
            box-shadow: 0 1px 1px rgba(17, 27, 33, 0.08);
        }
        .wa-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #8696a0;
            animation: wa-bounce 1.2s infinite ease-in-out;
        }
        .wa-dot:nth-child(2) {
            animation-delay: 0.15s;
        }
        .wa-dot:nth-child(3) {
            animation-delay: 0.3s;
        }
        @keyframes wa-bounce {
            0%, 80%, 100% { transform: translateY(0); opacity: 0.55; }
            40% { transform: translateY(-4px); opacity: 1; }
        }
        .wa-actions {
            padding: 12px 16px 2px;
            background: #f0f2f5;
            border-top: 1px solid rgba(31, 41, 51, 0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def current_time_label() -> str:
    return datetime.now().strftime("%H:%M")


def next_slot_datetime(slot_label: str) -> datetime:
    day_name, hour_text = slot_label.split()
    target_weekday = WEEKDAY_INDEX[day_name]
    hour, minute = map(int, hour_text.split(":"))
    now = datetime.now()
    days_ahead = (target_weekday - now.weekday()) % 7
    candidate = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=7)
    return candidate


def slot_display_label(slot_label: str) -> str:
    slot_dt = next_slot_datetime(slot_label)
    return f"{slot_label} ({slot_dt.strftime('%d %b %Y')})"


def parse_preferences(message: str) -> list[str]:
    profile = st.session_state.lead_profile
    normalized = message.lower()
    updated_fields = []

    phone_match = re.search(r"(\+?\d[\d\s\-]{7,}\d)", message)
    if phone_match:
        phone = re.sub(r"\s+", " ", phone_match.group(1)).strip()
        if profile["phone"] != phone:
            profile["phone"] = phone
            updated_fields.append("phone")

    name_patterns = [
        r"\bmy name is\s+([A-Za-z][A-Za-z\s'-]{1,40})",
        r"\bi am\s+([A-Za-z][A-Za-z\s'-]{1,40})",
        r"\bi'm\s+([A-Za-z][A-Za-z\s'-]{1,40})",
        r"\bthis is\s+([A-Za-z][A-Za-z\s'-]{1,40})",
    ]
    for pattern in name_patterns:
        name_match = re.search(pattern, message, re.IGNORECASE)
        if name_match:
            candidate = name_match.group(1).strip(" .,!?:;")
            candidate_words = candidate.split()
            if 1 <= len(candidate_words) <= 4 and not any(char.isdigit() for char in candidate):
                name = " ".join(word.capitalize() for word in candidate_words)
                if profile["name"] != name:
                    profile["name"] = name
                    updated_fields.append("name")
                break

    budget_match = re.search(r"(?:eur)?\s?(\d+(?:[\.,]\d+)?)\s?(k|m|million)?", normalized)
    if budget_match:
        raw = float(budget_match.group(1).replace(",", "."))
        suffix = budget_match.group(2)
        budget_keywords = ["budget", "around", "up to", "maximum", "max", "price range"]
        has_currency_cue = "eur" in normalized or suffix is not None
        has_budget_context = any(keyword in normalized for keyword in budget_keywords)
        number_token = budget_match.group(1)
        looks_like_phone_number = (
            suffix is None
            and "." not in number_token
            and "," not in number_token
            and len(re.sub(r"\D", "", number_token)) >= 8
            and not has_currency_cue
            and not has_budget_context
        )
        if suffix in {"m", "million"}:
            budget = round(raw * 1_000_000)
        elif suffix == "k":
            budget = round(raw * 1_000)
        elif looks_like_phone_number:
            budget = None
        elif has_currency_cue or has_budget_context or raw >= 50000:
            budget = round(raw)
        else:
            budget = None
        if budget and budget >= 50_000:
            if profile["budget"] != budget:
                profile["budget"] = budget
                updated_fields.append("budget")

    bedroom_match = re.search(r"(\d)\s*bed", normalized)
    if bedroom_match:
        bedrooms = int(bedroom_match.group(1))
        if profile["bedrooms"] != bedrooms:
            profile["bedrooms"] = bedrooms
            updated_fields.append("bedrooms")

    known_locations = [
        "strovolos",
        "lakatamia",
        "limassol",
        "engomi",
        "aglantzia",
        "archangelos",
        "nicosia",
        "dasoupoli",
        "germasogeia",
    ]
    found_location = next((value for value in known_locations if value in normalized), None)
    if found_location:
        location = found_location.capitalize()
        location_change_cues = [
            "change to",
            "switch to",
            "instead",
            "rather",
            "prefer",
            "focus on",
            "move to",
            "search in",
            "look in",
            "actually",
        ]
        can_update_location = (
            profile["location"] is None
            or profile["location"] == location
            or any(cue in normalized for cue in location_change_cues)
        )
        if can_update_location and profile["location"] != location:
            profile["location"] = location
            updated_fields.append("location")

    if "apartment" in normalized:
        if profile["purpose"] != "Apartment":
            profile["purpose"] = "Apartment"
            updated_fields.append("purpose")
    elif "house" in normalized or "home" in normalized:
        if profile["purpose"] != "House":
            profile["purpose"] = "House"
            updated_fields.append("purpose")
    elif "villa" in normalized:
        if profile["purpose"] != "Villa":
            profile["purpose"] = "Villa"
            updated_fields.append("purpose")

    timeline_signals = ["this month", "next month", "asap", "soon", "3 months", "six months", "investment"]
    found_timeline = next((value for value in timeline_signals if value in normalized), None)
    if found_timeline:
        if profile["timeline"] != found_timeline:
            profile["timeline"] = found_timeline
            updated_fields.append("timeline")

    if any(term in normalized for term in ["invest", "rental yield", "return", "investment"]):
        if profile["intent"] != "Investment":
            profile["intent"] = "Investment"
            updated_fields.append("intent")
    elif any(term in normalized for term in ["family", "live in", "move in", "home for us", "primary residence"]):
        if profile["intent"] != "Primary residence":
            profile["intent"] = "Primary residence"
            updated_fields.append("intent")

    return updated_fields


def get_listing_score(listing: dict) -> int:
    profile = st.session_state.lead_profile
    score = 0

    if profile["location"]:
        if listing["location"] == profile["location"]:
            score += 4
        elif profile["location"] == "Nicosia" and listing["location"] != "Limassol":
            score += 2

    if profile["budget"]:
        delta = abs(listing["price"] - profile["budget"])
        if delta <= profile["budget"] * 0.08:
            score += 4
        elif delta <= profile["budget"] * 0.2:
            score += 2

    if profile["bedrooms"]:
        if listing["bedrooms"] == profile["bedrooms"]:
            score += 3
        elif abs(listing["bedrooms"] - profile["bedrooms"]) == 1:
            score += 1

    if profile["purpose"] and profile["purpose"].lower() in listing["type"].lower():
        score += 3

    return score


def get_recommendations(prefer_fresh: bool = True) -> list[dict]:
    scored = sorted(
        LISTINGS,
        key=lambda listing: (-get_listing_score(listing), listing["price"]),
    )

    if not prefer_fresh:
        picks = scored[:3]
    else:
        unseen = [listing for listing in scored if listing["id"] not in st.session_state.shown_listing_ids]
        seen = [listing for listing in scored if listing["id"] in st.session_state.shown_listing_ids]
        picks = (unseen + seen)[:3]

    for listing in picks:
        if listing["id"] not in st.session_state.shown_listing_ids:
            st.session_state.shown_listing_ids.append(listing["id"])

    return picks


def profile_strength() -> int:
    profile = st.session_state.lead_profile
    score = 0
    for field in ["name", "phone", "budget", "location", "bedrooms", "purpose", "timeline", "intent"]:
        if profile.get(field):
            score += 1
    return score


def get_missing_qualifiers() -> list[str]:
    profile = st.session_state.lead_profile
    missing = []
    if not profile["budget"]:
        missing.append("budget")
    if not profile["location"]:
        missing.append("preferred location")
    if not profile["timeline"]:
        missing.append("timeline")
    return missing


def render_recommendations(matches: list[dict]) -> str:
    lines = []
    for index, listing in enumerate(matches, start=1):
        lead_note = ""
        if index == 1:
            lead_note = "Best fit right now"
        elif index == 2:
            lead_note = "Strong alternative"
        else:
            lead_note = "Worth comparing"
        lines.append(
            f"**{index}. {listing['title']}**\n"
            f"{lead_note} | {listing['price_label']} | {listing['bedrooms']} bedrooms | {listing['location']}\n"
            f"{listing['blurb']}"
        )
    return "\n".join(lines)


def get_next_question() -> tuple[str | None, str | None]:
    profile = st.session_state.lead_profile
    candidates = [
        (
            "name",
            "Before we go further, what name should I put on your inquiry?",
        ),
        (
            "phone",
            "What is the best phone number for viewing confirmation and follow-up?",
        ),
        (
            "budget",
            "What budget range would you like me to stay within?",
        ),
        (
            "location",
            "Which area should I focus on first, such as Strovolos, Lakatamia, Engomi, Limassol, or Germasogeia?",
        ),
        (
            "timeline",
            "How soon are you hoping to buy or arrange a viewing?",
        ),
        (
            "bedrooms",
            "How many bedrooms would feel right for you?",
        ),
        (
            "intent",
            "Is this mainly for your own use or more of an investment purchase?",
        ),
    ]

    for field, question in candidates:
        needs_value = field == "location" and not profile["location"]
        needs_value = needs_value or (field != "location" and not profile.get(field))
        if needs_value and field not in st.session_state.asked_fields:
            st.session_state.asked_fields.append(field)
            return field, question
    return None, None


def summarize_updates(updated_fields: list[str]) -> str:
    profile = st.session_state.lead_profile
    labels = []
    for field in updated_fields:
        if field == "name" and profile["name"]:
            labels.append(f"your name as {profile['name']}")
        elif field == "phone" and profile["phone"]:
            labels.append(f"your phone number as {profile['phone']}")
        if field == "budget" and profile["budget"]:
            labels.append(f"budget around EUR{profile['budget']:,}")
        elif field == "location" and profile["location"]:
            labels.append(f"focus on {profile['location']}")
        elif field == "timeline" and profile["timeline"]:
            labels.append(f"timeline {profile['timeline']}")
        elif field == "bedrooms" and profile["bedrooms"]:
            labels.append(f"{profile['bedrooms']} bedrooms")
        elif field == "purpose" and profile["purpose"]:
            labels.append(profile["purpose"].lower())
        elif field == "intent" and profile["intent"]:
            labels.append(profile["intent"].lower())

    if not labels:
        return ""
    if len(labels) == 1:
        return f"Understood, I have noted {labels[0]}."
    return "Understood, I have noted " + ", ".join(labels[:-1]) + f", and {labels[-1]}."


def should_offer_booking() -> bool:
    profile = st.session_state.lead_profile
    populated = sum(
        1 for key in ["name", "phone", "budget", "location", "timeline", "bedrooms", "purpose", "intent"] if profile.get(key)
    )
    return populated >= 5


def next_phrase(kind: str, options: list[str]) -> str:
    counters = st.session_state.response_counters
    index = counters[kind] % len(options)
    counters[kind] += 1
    return options[index]


def mentions_booking(normalized: str) -> bool:
    return any(term in normalized for term in ["book", "viewing", "visit", "schedule", "calendar"])


def asks_for_recommendations(normalized: str) -> bool:
    return any(term in normalized for term in ["recommend", "suggest", "best option"])


def asks_for_similar(normalized: str) -> bool:
    return any(term in normalized for term in ["similar", "comparable", "alternatives"])


def asks_about_properties(normalized: str) -> bool:
    return any(term in normalized for term in ["property", "properties", "apartment", "house", "villa", "home", "listing"])


def try_book_specific_slot(normalized: str) -> bool:
    profile = st.session_state.lead_profile
    for slot in VIEWING_SLOTS:
        if slot.lower() in normalized:
            profile["viewing_booked"] = slot
            return True
    return False


def build_fallback() -> str:
    _, next_question = get_next_question()
    body = next_question or "If you want, I can now narrow this to a tighter shortlist or move straight to viewing times."
    return f"{next_phrase('fallback', FALLBACK_INTROS)}\n\n{body}"


def build_qualifying_reply(acknowledgment: str = "") -> str:
    _, next_question = get_next_question()
    prompt = next_question or "Share your budget, preferred area, and ideal bedroom count, and I will suggest the most relevant options."
    parts = [acknowledgment, next_phrase("fallback", QUALIFYING_INTROS), prompt]
    return "\n\n".join(part for part in parts if part)


def build_lead_json() -> dict:
    profile = st.session_state.lead_profile
    viewing_dt = next_slot_datetime(profile["viewing_booked"]).isoformat() if profile["viewing_booked"] else None
    return {
        "lead": {
            "name": profile["name"],
            "phone_number": profile["phone"],
            "budget": profile["budget"],
            "preferred_location": profile["location"],
            "timeline": profile["timeline"],
        },
        "meta": {
            "purpose": profile["purpose"],
            "intent": profile["intent"],
            "bedrooms": profile["bedrooms"],
            "selected_listing": profile["selected_listing"],
            "viewing_booked": profile["viewing_booked"],
            "viewing_datetime": viewing_dt,
            "captured_at": datetime.now().isoformat(timespec="seconds"),
        },
    }


def build_calendar_ics() -> str | None:
    profile = st.session_state.lead_profile
    if not profile["viewing_booked"]:
        return None

    start_dt = next_slot_datetime(profile["viewing_booked"])
    end_dt = start_dt + timedelta(minutes=45)
    lead_name = profile["name"] or "Prospective buyer"
    listing_name = profile["selected_listing"] or "M.Residence property viewing"
    phone = profile["phone"] or "Not provided"
    location = profile["location"] or "Cyprus"
    uid = f"mresidence-{start_dt.strftime('%Y%m%dT%H%M%S')}-{phone.replace(' ', '').replace('+', '')}@mresidence.demo"
    created = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    start_utc = start_dt.strftime("%Y%m%dT%H%M%S")
    end_utc = end_dt.strftime("%Y%m%dT%H%M%S")
    description = (
        f"Viewing arranged by M.Residence for {lead_name}.\\n"
        f"Property: {listing_name}\\n"
        f"Phone: {phone}\\n"
        f"Preferred area: {location}"
    )

    return "\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//M.Residence//AI Concierge//EN",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{created}",
            f"DTSTART:{start_utc}",
            f"DTEND:{end_utc}",
            f"SUMMARY:M.Residence Viewing - {listing_name}",
            f"DESCRIPTION:{description}",
            f"LOCATION:{location}, Cyprus",
            "END:VEVENT",
            "END:VCALENDAR",
        ]
    )


def confirm_viewing_slot(slot_label: str, source: str = "booking widget") -> None:
    profile = st.session_state.lead_profile
    profile["viewing_booked"] = slot_label
    if not profile["selected_listing"]:
        shortlist = get_recommendations(prefer_fresh=False)
        if shortlist:
            profile["selected_listing"] = shortlist[0]["title"]

    confirmation = (
        f"Perfect, I have reserved **{slot_display_label(slot_label)}** for your viewing.\n\n"
        f"I have linked it to **{profile['selected_listing'] or 'your shortlisted property'}** and prepared the calendar event for download."
    )
    st.session_state.messages.append({"role": "assistant", "content": confirmation, "time": current_time_label()})
    maybe_send_lead_to_webhook()


def get_webhook_url() -> str | None:
    try:
        secrets_url = st.secrets.get("lead_webhook_url")
        if secrets_url:
            return secrets_url
    except Exception:
        pass
    return os.getenv("LEAD_WEBHOOK_URL")


def get_notification_webhook_url() -> str | None:
    try:
        secrets_url = st.secrets.get("agent_notification_webhook_url")
        if secrets_url:
            return secrets_url
    except Exception:
        pass
    return os.getenv("AGENT_NOTIFICATION_WEBHOOK_URL")


def lead_ready_for_webhook() -> bool:
    profile = st.session_state.lead_profile
    required = ["name", "phone", "budget", "location", "timeline"]
    has_required = all(profile.get(field) for field in required)
    strong_interest = bool(profile.get("viewing_booked") or profile.get("selected_listing"))
    return has_required and strong_interest


def lead_fingerprint(payload: dict) -> str:
    lead = payload["lead"]
    meta = payload["meta"]
    return "|".join(
        [
            str(lead.get("name")),
            str(lead.get("phone_number")),
            str(lead.get("budget")),
            str(lead.get("preferred_location")),
            str(lead.get("timeline")),
            str(meta.get("selected_listing")),
            str(meta.get("viewing_booked")),
        ]
    )


def build_notification_payload() -> dict:
    lead_payload = build_lead_json()
    profile = st.session_state.lead_profile
    return {
        "type": "new_real_estate_lead",
        "agency": "M.Residence",
        "message": (
            f"New lead from {profile['name'] or 'unknown lead'} | "
            f"Phone: {profile['phone'] or 'not provided'} | "
            f"Budget: {('EUR' + format(profile['budget'], ',')) if profile['budget'] else 'not provided'} | "
            f"Location: {profile['location'] or 'not provided'} | "
            f"Timeline: {profile['timeline'] or 'not provided'}"
        ),
        "lead_json": lead_payload,
    }


def get_best_matches_for_follow_up() -> list[dict]:
    return get_recommendations(prefer_fresh=False)


def build_follow_up_schedule() -> list[dict]:
    profile = st.session_state.lead_profile
    lead_name = profile["name"] or "there"
    budget_text = f"around EUR{profile['budget']:,}" if profile["budget"] else "within your target budget"
    location_text = profile["location"] or "your preferred area"
    timeline_text = profile["timeline"] or "your timeframe"
    best_matches = get_best_matches_for_follow_up()
    top_listing = best_matches[0]["title"] if best_matches else "the shortlisted property"
    alternatives = ", ".join(listing["title"] for listing in best_matches[1:3]) if len(best_matches) > 1 else "a couple of comparable homes"
    created_at = datetime.now()

    return [
        {
            "day": 1,
            "scheduled_for": (created_at + timedelta(days=1)).isoformat(timespec="seconds"),
            "channel": "email_or_message",
            "message": (
                f"Hi {lead_name}, this is M.Residence checking in on your interest in {top_listing}. "
                f"Would you like me to keep searching in {location_text} with a budget {budget_text}, "
                f"or would you prefer to move toward arranging a viewing?"
            ),
        },
        {
            "day": 3,
            "scheduled_for": (created_at + timedelta(days=3)).isoformat(timespec="seconds"),
            "channel": "email_or_message",
            "message": (
                f"Hi {lead_name}, I have pulled together a few similar options that may suit your plans for {timeline_text}. "
                f"Alongside {top_listing}, I would suggest looking at {alternatives}. "
                "If you want, I can send a tighter comparison and recommended next step."
            ),
        },
        {
            "day": 7,
            "scheduled_for": (created_at + timedelta(days=7)).isoformat(timespec="seconds"),
            "channel": "email_or_message",
            "message": (
                f"Hi {lead_name}, I wanted to re-engage with a fresh set of options in {location_text}. "
                f"I still have your brief saved with a budget {budget_text}, and I can send updated recommendations or arrange a new viewing slot if the timing now works better for you."
            ),
        },
    ]


def build_follow_up_payload() -> dict:
    return {
        "type": "lead_follow_up_schedule",
        "agency": "M.Residence",
        "lead_json": build_lead_json(),
        "follow_ups": build_follow_up_schedule(),
    }


def send_follow_up_plan(force: bool = False) -> tuple[bool, str]:
    notification_url = get_notification_webhook_url()
    if not notification_url:
        message = "Notification webhook not configured"
        st.session_state.follow_up_status = message
        return False, message

    payload = build_follow_up_payload()
    fingerprint = lead_fingerprint(payload["lead_json"]) + "|follow-up"

    if not force and st.session_state.last_follow_up_fingerprint == fingerprint:
        message = "Follow-up plan already sent"
        st.session_state.follow_up_status = message
        return True, message

    request = urllib.request.Request(
        notification_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            status_code = response.getcode()
        if 200 <= status_code < 300:
            st.session_state.last_follow_up_fingerprint = fingerprint
            message = f"Follow-up plan sent ({status_code})"
            st.session_state.follow_up_status = message
            return True, message
        message = f"Follow-up webhook returned status {status_code}"
        st.session_state.follow_up_status = message
        return False, message
    except urllib.error.HTTPError as error:
        message = f"Follow-up error {error.code}"
        st.session_state.follow_up_status = message
        return False, message
    except Exception as error:
        message = f"Follow-up failed: {error}"
        st.session_state.follow_up_status = message
        return False, message


def send_agent_notification(force: bool = False) -> tuple[bool, str]:
    notification_url = get_notification_webhook_url()
    if not notification_url:
        message = "Notification webhook not configured"
        st.session_state.notification_status = message
        return False, message

    payload = build_notification_payload()
    fingerprint = lead_fingerprint(payload["lead_json"])

    if not force and st.session_state.last_notification_fingerprint == fingerprint:
        message = "Notification already sent"
        st.session_state.notification_status = message
        return True, message

    request = urllib.request.Request(
        notification_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            status_code = response.getcode()
        if 200 <= status_code < 300:
            st.session_state.last_notification_fingerprint = fingerprint
            message = f"Notification sent ({status_code})"
            st.session_state.notification_status = message
            return True, message
        message = f"Notification webhook returned status {status_code}"
        st.session_state.notification_status = message
        return False, message
    except urllib.error.HTTPError as error:
        message = f"Notification error {error.code}"
        st.session_state.notification_status = message
        return False, message
    except Exception as error:
        message = f"Notification failed: {error}"
        st.session_state.notification_status = message
        return False, message


def send_lead_to_webhook(force: bool = False) -> tuple[bool, str]:
    webhook_url = get_webhook_url()
    if not webhook_url:
        message = "Webhook URL not configured"
        st.session_state.webhook_status = message
        return False, message

    payload = build_lead_json()
    fingerprint = lead_fingerprint(payload)

    if not force and st.session_state.last_sent_fingerprint == fingerprint:
        message = "Lead already sent"
        st.session_state.webhook_status = message
        return True, message

    request = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            status_code = response.getcode()
        if 200 <= status_code < 300:
            st.session_state.last_sent_fingerprint = fingerprint
            message = f"Sent to webhook ({status_code})"
            st.session_state.webhook_status = message
            return True, message
        message = f"Webhook returned status {status_code}"
        st.session_state.webhook_status = message
        return False, message
    except urllib.error.HTTPError as error:
        message = f"Webhook error {error.code}"
        st.session_state.webhook_status = message
        return False, message
    except Exception as error:
        message = f"Webhook failed: {error}"
        st.session_state.webhook_status = message
        return False, message


def maybe_send_lead_to_webhook() -> None:
    if lead_ready_for_webhook():
        send_lead_to_webhook()
        send_agent_notification()
        send_follow_up_plan()


def generate_reply(message: str) -> str:
    profile = st.session_state.lead_profile
    normalized = message.lower()
    updated_fields = parse_preferences(message)
    acknowledgment = summarize_updates(updated_fields)

    if try_book_specific_slot(normalized):
        selected = profile["selected_listing"] or "the shortlisted property"
        response = (
            f"Perfect, I have penciled you in for **{profile['viewing_booked']}**.\n\n"
            f"I will note your interest in **{selected}**. Before the viewing, would you like me to suggest one or two comparable options so you can compare value on the same trip?"
        )
        maybe_send_lead_to_webhook()
        return response

    if mentions_booking(normalized):
        if profile_strength() < 3:
            parts = [
                acknowledgment,
                "I can absolutely help arrange that.",
                "Before I suggest the best slot and property, I just need one or two details so I do not book you against the wrong type of home.",
                get_next_question()[1] or "What budget and area should I work with?",
            ]
            return "\n\n".join(part for part in parts if part)
        shortlist = get_recommendations(prefer_fresh=False)
        if shortlist:
            profile["selected_listing"] = shortlist[0]["title"]
            lead_line = (
                f"The strongest fit so far is **{shortlist[0]['title']}** at **{shortlist[0]['price_label']}**."
            )
        else:
            lead_line = "I can arrange that for you."
        slots = ", ".join(VIEWING_SLOTS)
        parts = [
            acknowledgment,
            f"Absolutely. {lead_line}\n\n"
            f"Here are a few viewing times available this week: **{slots}**.\n\n"
            "Reply with the time that works best and I will confirm it for you."
        ]
        response = "\n\n".join(part for part in parts if part)
        maybe_send_lead_to_webhook()
        return response

    if asks_for_similar(normalized) or asks_for_recommendations(normalized):
        if profile_strength() < 3:
            return build_qualifying_reply(acknowledgment)
        matches = get_recommendations()
        if matches:
            profile["selected_listing"] = matches[0]["title"]
            closing = (
                "If one stands out, I can line up a viewing and give you two comparables for context."
                if should_offer_booking()
                else get_next_question()[1] or "If you want, I can refine this further by area, budget, or timing."
            )
            parts = [
                acknowledgment,
                f"{next_phrase('recommend', RECOMMENDATION_INTROS)}\n\n"
                f"{render_recommendations(matches)}\n\n"
                "The first option is the strongest fit, and the next two give you strong alternatives on price or location.",
                closing,
            ]
            response = "\n\n".join(part for part in parts if part)
            maybe_send_lead_to_webhook()
            return response
        return build_fallback()

    if asks_about_properties(normalized) or profile["location"] or profile["budget"] or profile["bedrooms"]:
        if profile_strength() < 3:
            return build_qualifying_reply(acknowledgment)
        matches = get_recommendations()
        _, next_question = get_next_question()
        if next_question:
            follow_up = next_question
        elif should_offer_booking():
            follow_up = "If you would like, I can now line up a viewing or show you two comparable options in the same bracket."
        else:
            follow_up = "If you want, give me one more detail and I will tighten the shortlist further."
        if matches:
            profile["selected_listing"] = matches[0]["title"]
            parts = [
                acknowledgment,
                f"{next_phrase('property', PROPERTY_INTROS)}\n\n"
                f"{render_recommendations(matches)}\n\n"
                f"{follow_up}",
            ]
            response = "\n\n".join(part for part in parts if part)
            maybe_send_lead_to_webhook()
            return response
        return build_fallback()

    fallback = build_fallback()
    return "\n\n".join(part for part in [acknowledgment, fallback] if part)


def reset_chat() -> None:
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME_MESSAGE, "time": current_time_label()}
    ]
    st.session_state.lead_profile = deepcopy(INITIAL_PROFILE)
    st.session_state.shown_listing_ids = []
    st.session_state.response_counters = {"recommend": 0, "property": 0, "fallback": 0}
    st.session_state.asked_fields = []
    st.session_state.pending_reply = None
    st.session_state.webhook_status = "Not sent"
    st.session_state.last_sent_fingerprint = None
    st.session_state.notification_status = "Not sent"
    st.session_state.last_notification_fingerprint = None
    st.session_state.follow_up_status = "Not sent"
    st.session_state.last_follow_up_fingerprint = None


def submit_prompt(prompt: str) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt, "time": current_time_label()})
    st.session_state.pending_reply = generate_reply(prompt)


def flush_pending_reply() -> None:
    if st.session_state.pending_reply:
        time.sleep(0.55)
        st.session_state.messages.append(
            {"role": "assistant", "content": st.session_state.pending_reply, "time": current_time_label()}
        )
        st.session_state.pending_reply = None


def render_chat_thread() -> None:
    st.markdown(
        """
        <div class="wa-shell">
          <div class="wa-header">
            <div class="wa-agent">
              <div class="wa-avatar">MR</div>
              <div>
                <div class="wa-name">M.Residence Concierge</div>
                <div class="wa-status">online now</div>
              </div>
            </div>
            <div class="wa-status">WhatsApp-style demo</div>
          </div>
          <div class="wa-thread">
        """,
        unsafe_allow_html=True,
    )

    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"].replace("\n", "<br>")
        st.markdown(
            f"""
            <div class="wa-row {role}">
              <div class="wa-bubble">
                {content}
                <span class="wa-time">{message.get("time", "")}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.pending_reply:
        st.markdown(
            """
            <div class="wa-row assistant">
              <div class="wa-typing">
                <span class="wa-dot"></span>
                <span class="wa-dot"></span>
                <span class="wa-dot"></span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div></div>", unsafe_allow_html=True)


def render_featured_listings() -> None:
    for listing in LISTINGS[:3]:
        tags = "".join(f"<span class='tag'>{tag}</span>" for tag in listing["tags"])
        st.markdown(
            f"""
            <div class="listing-card">
              <div class="listing-title">{listing["title"]}</div>
              <div class="listing-meta">{listing["type"]} | {listing["bedrooms"]} bedrooms | {listing["location"]}</div>
              <div class="listing-meta listing-price">{listing["price_label"]}</div>
              <div class="listing-blurb">{listing["blurb"]}</div>
              <div>{tags}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_profile() -> None:
    profile = st.session_state.lead_profile
    name = profile["name"] or "Not captured yet"
    phone = profile["phone"] or "Not captured yet"
    budget = f"EUR{profile['budget']:,}" if profile["budget"] else "Not captured yet"
    location = profile["location"] or "Not captured yet"
    timeline = profile["timeline"] or "Not captured yet"
    bedrooms = str(profile["bedrooms"]) if profile["bedrooms"] else "Flexible"
    intent = profile["intent"] or "Not captured yet"
    selected = profile["selected_listing"] or "No current lead property"
    viewing = profile["viewing_booked"] or "No viewing booked"

    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("### Lead Snapshot")
    st.markdown(f"**Name:** {name}")
    st.markdown(f"**Phone:** {phone}")
    st.markdown(f"**Budget:** {budget}")
    st.markdown(f"**Location:** {location}")
    st.markdown(f"**Timeline:** {timeline}")
    st.markdown(f"**Bedrooms:** {bedrooms}")
    st.markdown(f"**Use case:** {intent}")
    st.markdown(f"**Current best match:** {selected}")
    st.markdown(f"**Viewing status:** {viewing}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("### Suggested viewing times")
    slots_html = "".join(f"<span class='slot'>{slot_display_label(slot)}</span>" for slot in VIEWING_SLOTS)
    st.markdown(slots_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("### Book Viewing")
    selected_slot = st.selectbox(
        "Available time slots",
        options=VIEWING_SLOTS,
        format_func=slot_display_label,
        key="viewing_slot_picker",
    )
    if st.button("Confirm viewing time", use_container_width=True):
        confirm_viewing_slot(selected_slot)
        st.rerun()

    if profile["viewing_booked"]:
        st.markdown(f"**Confirmed slot:** {slot_display_label(profile['viewing_booked'])}")
        calendar_ics = build_calendar_ics()
        if calendar_ics:
            event_name = (profile["selected_listing"] or "m_residence_viewing").replace(" ", "_").lower()
            st.download_button(
                "Add calendar event (.ics)",
                data=calendar_ics,
                file_name=f"{event_name}.ics",
                mime="text/calendar",
                use_container_width=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    lead_json = build_lead_json()
    follow_up_plan = build_follow_up_schedule()
    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("### Lead JSON")
    st.code(json.dumps(lead_json, indent=2), language="json")
    st.download_button(
        "Download lead JSON",
        data=json.dumps(lead_json, indent=2),
        file_name="m_residence_lead.json",
        mime="application/json",
        use_container_width=True,
    )
    webhook_configured = "Yes" if get_webhook_url() else "No"
    notification_configured = "Yes" if get_notification_webhook_url() else "No"
    st.markdown(f"**Webhook configured:** {webhook_configured}")
    st.markdown(f"**Webhook status:** {st.session_state.webhook_status}")
    st.markdown(f"**Notification webhook configured:** {notification_configured}")
    st.markdown(f"**Notification status:** {st.session_state.notification_status}")
    st.markdown(f"**Follow-up status:** {st.session_state.follow_up_status}")
    if st.button("Send Lead To Google Sheet", use_container_width=True):
        send_lead_to_webhook(force=True)
        st.rerun()
    if st.button("Send Agent Notification", use_container_width=True):
        send_agent_notification(force=True)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("### Automated Follow-Ups")
    for item in follow_up_plan:
        st.markdown(
            f"**Day {item['day']}** | {item['scheduled_for']}\n\n{item['message']}"
        )
    st.code(json.dumps(build_follow_up_payload(), indent=2), language="json")
    if st.button("Send Follow-Up Plan", use_container_width=True):
        send_follow_up_plan(force=True)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


init_state()
inject_styles()

left_col, right_col = st.columns([1.02, 1], gap="large")

with left_col:
    st.markdown(
        """
        <div class="panel">
          <p class="eyebrow">M.Residence Cyprus</p>
          <h1 class="hero-title">AI real estate assistant for high-conversion property demos.</h1>
          <p class="hero-copy">
            A friendly, professional chatbot that qualifies leads, recommends matching homes,
            and smoothly moves buyers toward booking a viewing.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='panel' style='margin-top:16px;'>", unsafe_allow_html=True)
    st.markdown("### Featured listings")
    render_featured_listings()
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("### M.Residence Concierge")
    st.caption("WhatsApp-style demo chat with simulated live responses.")

    quick_prompts = [
        "I'm looking for an apartment in Strovolos around EUR260,000.",
        "Show me family homes in Nicosia with 3 bedrooms.",
        "I want to book a viewing this week.",
    ]

    quick_cols = st.columns(3)
    for index, prompt in enumerate(quick_prompts):
        if quick_cols[index].button(prompt.split(".")[0], use_container_width=True):
            submit_prompt(prompt)
            flush_pending_reply()
            st.rerun()

    render_chat_thread()

    user_prompt = st.chat_input("Ask about homes, budget, areas, or book a viewing...")
    if user_prompt:
        submit_prompt(user_prompt)
        flush_pending_reply()
        st.rerun()

    if st.button("Reset conversation", use_container_width=True):
        reset_chat()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    render_profile()
