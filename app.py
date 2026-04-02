import re
from copy import deepcopy

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
]

VIEWING_SLOTS = [
    "Tuesday 11:00",
    "Tuesday 16:30",
    "Wednesday 12:15",
    "Thursday 10:00",
    "Friday 15:45",
]

INITIAL_PROFILE = {
    "budget": None,
    "location": None,
    "timeline": None,
    "bedrooms": None,
    "purpose": None,
    "selected_listing": None,
    "viewing_booked": None,
}

WELCOME_MESSAGE = (
    "Welcome to **M.Residence**. I can help you explore homes in Cyprus, narrow down the right fit, "
    "and line up a viewing.\n\n"
    "To get started, are you mainly looking for an apartment, house, or villa, and which area is top of mind?"
)


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]
    if "lead_profile" not in st.session_state:
        st.session_state.lead_profile = deepcopy(INITIAL_PROFILE)


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
        </style>
        """,
        unsafe_allow_html=True,
    )


def parse_preferences(message: str) -> None:
    profile = st.session_state.lead_profile
    normalized = message.lower()

    budget_match = re.search(r"(?:eur)?\s?(\d+(?:[\.,]\d+)?)\s?(k|m|million)?", normalized)
    if budget_match:
        raw = float(budget_match.group(1).replace(",", "."))
        suffix = budget_match.group(2)
        if suffix in {"m", "million"}:
            budget = round(raw * 1_000_000)
        elif suffix == "k":
            budget = round(raw * 1_000)
        elif raw < 10:
            budget = round(raw * 100_000)
        else:
            budget = round(raw)
        if budget >= 50_000:
            profile["budget"] = budget

    bedroom_match = re.search(r"(\d)\s*bed", normalized)
    if bedroom_match:
        profile["bedrooms"] = int(bedroom_match.group(1))

    known_locations = [
        "strovolos",
        "lakatamia",
        "limassol",
        "engomi",
        "aglantzia",
        "archangelos",
        "nicosia",
    ]
    found_location = next((value for value in known_locations if value in normalized), None)
    if found_location:
        profile["location"] = found_location.capitalize()

    if "apartment" in normalized:
        profile["purpose"] = "Apartment"
    elif "house" in normalized or "home" in normalized:
        profile["purpose"] = "House"
    elif "villa" in normalized:
        profile["purpose"] = "Villa"

    timeline_signals = ["this month", "next month", "asap", "soon", "3 months", "six months", "investment"]
    found_timeline = next((value for value in timeline_signals if value in normalized), None)
    if found_timeline:
        profile["timeline"] = found_timeline


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


def get_recommendations() -> list[dict]:
    scored = sorted(
        LISTINGS,
        key=lambda listing: (-get_listing_score(listing), listing["price"]),
    )
    return scored[:3]


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
    for listing in matches:
        lines.append(
            f"- **{listing['title']}** | {listing['price_label']}\n"
            f"  {listing['bedrooms']} bedrooms | {listing['location']} | {listing['blurb']}"
        )
    return "\n".join(lines)


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
    missing = get_missing_qualifiers()
    if missing:
        prompt = f"A quick way for me to narrow it down is your {', '.join(missing[:3])}."
    else:
        prompt = "I already have enough to start matching options."

    return (
        "I can help with search, comparisons, or a viewing arrangement.\n\n"
        f"{prompt}\n\n"
        "For example: **I want a 3 bedroom house in Lakatamia around EUR400,000 and I would like to move within 3 months.**"
    )


def generate_reply(message: str) -> str:
    profile = st.session_state.lead_profile
    normalized = message.lower()
    parse_preferences(message)

    if try_book_specific_slot(normalized):
        selected = profile["selected_listing"] or "the shortlisted property"
        return (
            f"Perfect, I have penciled you in for **{profile['viewing_booked']}**.\n\n"
            f"I will note your interest in **{selected}**. Before the viewing, would you like me to suggest one or two comparable options so you can compare value on the same trip?"
        )

    if mentions_booking(normalized):
        shortlist = get_recommendations()
        if shortlist:
            profile["selected_listing"] = shortlist[0]["title"]
            lead_line = (
                f"The strongest fit so far is **{shortlist[0]['title']}** at **{shortlist[0]['price_label']}**."
            )
        else:
            lead_line = "I can arrange that for you."
        slots = ", ".join(VIEWING_SLOTS)
        return (
            f"Absolutely. {lead_line}\n\n"
            f"Here are a few viewing times available this week: **{slots}**.\n\n"
            "Reply with the time that works best and I will confirm it for you."
        )

    if asks_for_similar(normalized) or asks_for_recommendations(normalized):
        matches = get_recommendations()
        if matches:
            profile["selected_listing"] = matches[0]["title"]
            return (
                "Here are the closest matches I would suggest based on what you have shared:\n\n"
                f"{render_recommendations(matches)}\n\n"
                "The first option is the strongest fit, and the next two give you strong alternatives on price or location."
            )
        return build_fallback()

    if asks_about_properties(normalized) or profile["location"] or profile["budget"] or profile["bedrooms"]:
        matches = get_recommendations()
        missing = get_missing_qualifiers()
        follow_up = (
            f"To refine this properly, could you also share your {' and '.join(missing[:2])}?"
            if missing
            else "Would you like me to line up a viewing or show you a couple of comparable alternatives in the same bracket?"
        )
        if matches:
            profile["selected_listing"] = matches[0]["title"]
            return (
                "Based on your brief, these are the properties I would put forward first:\n\n"
                f"{render_recommendations(matches)}\n\n"
                f"{follow_up}"
            )
        return build_fallback()

    return build_fallback()


def reset_chat() -> None:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]
    st.session_state.lead_profile = deepcopy(INITIAL_PROFILE)


def submit_prompt(prompt: str) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    reply = generate_reply(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})


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
    budget = f"EUR{profile['budget']:,}" if profile["budget"] else "Not captured yet"
    location = profile["location"] or "Not captured yet"
    timeline = profile["timeline"] or "Not captured yet"
    bedrooms = str(profile["bedrooms"]) if profile["bedrooms"] else "Flexible"
    selected = profile["selected_listing"] or "No current lead property"
    viewing = profile["viewing_booked"] or "No viewing booked"

    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("### Lead Snapshot")
    st.markdown(f"**Budget:** {budget}")
    st.markdown(f"**Location:** {location}")
    st.markdown(f"**Timeline:** {timeline}")
    st.markdown(f"**Bedrooms:** {bedrooms}")
    st.markdown(f"**Current best match:** {selected}")
    st.markdown(f"**Viewing status:** {viewing}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("### Suggested viewing times")
    slots_html = "".join(f"<span class='slot'>{slot}</span>" for slot in VIEWING_SLOTS)
    st.markdown(slots_html, unsafe_allow_html=True)
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
    st.caption("Friendly, professional, slightly conversational. No login required.")

    quick_prompts = [
        "I'm looking for an apartment in Strovolos around EUR260,000.",
        "Show me family homes in Nicosia with 3 bedrooms.",
        "I want to book a viewing this week.",
    ]

    quick_cols = st.columns(3)
    for index, prompt in enumerate(quick_prompts):
        if quick_cols[index].button(prompt.split(".")[0], use_container_width=True):
            submit_prompt(prompt)
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask about homes, budget, areas, or book a viewing...")
    if user_prompt:
        submit_prompt(user_prompt)
        st.rerun()

    if st.button("Reset conversation", use_container_width=True):
        reset_chat()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    render_profile()
