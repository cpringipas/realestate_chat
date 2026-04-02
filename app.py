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

INITIAL_PROFILE = {
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
    if "shown_listing_ids" not in st.session_state:
        st.session_state.shown_listing_ids = []
    if "response_counters" not in st.session_state:
        st.session_state.response_counters = {"recommend": 0, "property": 0, "fallback": 0}
    if "asked_fields" not in st.session_state:
        st.session_state.asked_fields = []


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


def parse_preferences(message: str) -> list[str]:
    profile = st.session_state.lead_profile
    normalized = message.lower()
    updated_fields = []

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
        if profile["location"] != location:
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


def get_next_question() -> tuple[str | None, str | None]:
    profile = st.session_state.lead_profile
    candidates = [
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
        1 for key in ["budget", "location", "timeline", "bedrooms", "purpose", "intent"] if profile.get(key)
    )
    return populated >= 3


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


def generate_reply(message: str) -> str:
    profile = st.session_state.lead_profile
    normalized = message.lower()
    updated_fields = parse_preferences(message)
    acknowledgment = summarize_updates(updated_fields)

    if try_book_specific_slot(normalized):
        selected = profile["selected_listing"] or "the shortlisted property"
        return (
            f"Perfect, I have penciled you in for **{profile['viewing_booked']}**.\n\n"
            f"I will note your interest in **{selected}**. Before the viewing, would you like me to suggest one or two comparable options so you can compare value on the same trip?"
        )

    if mentions_booking(normalized):
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
        return "\n\n".join(part for part in parts if part)

    if asks_for_similar(normalized) or asks_for_recommendations(normalized):
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
            return "\n\n".join(part for part in parts if part)
        return build_fallback()

    if asks_about_properties(normalized) or profile["location"] or profile["budget"] or profile["bedrooms"]:
        matches = get_recommendations()
        _, next_question = get_next_question()
        if next_question:
            follow_up = next_question
        elif should_offer_booking():
            follow_up = "Would you like me to line up a viewing or show you a couple of comparable alternatives in the same bracket?"
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
            return "\n\n".join(part for part in parts if part)
        return build_fallback()

    fallback = build_fallback()
    return "\n\n".join(part for part in [acknowledgment, fallback] if part)


def reset_chat() -> None:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]
    st.session_state.lead_profile = deepcopy(INITIAL_PROFILE)
    st.session_state.shown_listing_ids = []
    st.session_state.response_counters = {"recommend": 0, "property": 0, "fallback": 0}
    st.session_state.asked_fields = []


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
    intent = profile["intent"] or "Not captured yet"
    selected = profile["selected_listing"] or "No current lead property"
    viewing = profile["viewing_booked"] or "No viewing booked"

    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("### Lead Snapshot")
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
