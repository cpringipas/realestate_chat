const listings = [
  {
    id: 1,
    title: "2 bedroom apartment in Strovolos",
    type: "Apartment",
    location: "Strovolos",
    bedrooms: 2,
    price: 250000,
    priceLabel: "EUR250,000",
    blurb: "Bright modern apartment close to schools, cafes, and central Nicosia access.",
    tags: ["Balcony", "Parking", "Ideal for first-time buyers"]
  },
  {
    id: 2,
    title: "3 bedroom house in Lakatamia",
    type: "House",
    location: "Lakatamia",
    bedrooms: 3,
    price: 380000,
    priceLabel: "EUR380,000",
    blurb: "Family-ready home with a private garden, covered parking, and quiet residential feel.",
    tags: ["Garden", "Family area", "Move-in ready"]
  },
  {
    id: 3,
    title: "Luxury villa in Limassol",
    type: "Villa",
    location: "Limassol",
    bedrooms: 4,
    price: 1200000,
    priceLabel: "EUR1.2M",
    blurb: "Premium sea-view villa with pool, designer interiors, and strong prestige appeal.",
    tags: ["Sea view", "Pool", "Luxury"]
  },
  {
    id: 4,
    title: "2 bedroom penthouse in Engomi",
    type: "Penthouse",
    location: "Engomi",
    bedrooms: 2,
    price: 315000,
    priceLabel: "EUR315,000",
    blurb: "Stylish penthouse with a large veranda and excellent rental potential near embassies.",
    tags: ["Penthouse", "Veranda", "Investment"]
  },
  {
    id: 5,
    title: "3 bedroom apartment in Aglantzia",
    type: "Apartment",
    location: "Aglantzia",
    bedrooms: 3,
    price: 295000,
    priceLabel: "EUR295,000",
    blurb: "Spacious city apartment well suited to growing families wanting quick Nicosia access.",
    tags: ["City access", "Large living area", "Near parks"]
  },
  {
    id: 6,
    title: "4 bedroom detached home in Archangelos",
    type: "House",
    location: "Archangelos",
    bedrooms: 4,
    price: 465000,
    priceLabel: "EUR465,000",
    blurb: "Detached home with generous indoor space and a refined suburban neighborhood profile.",
    tags: ["Detached", "Quiet area", "Parking"]
  }
];

const viewingSlots = [
  "Tuesday 11:00",
  "Tuesday 16:30",
  "Wednesday 12:15",
  "Thursday 10:00",
  "Friday 15:45"
];

const leadProfile = {
  budget: null,
  location: null,
  timeline: null,
  bedrooms: null,
  purpose: null,
  selectedListing: null,
  viewingBooked: null
};

const chatThread = document.getElementById("chatThread");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const featuredListings = document.getElementById("featuredListings");
const messageTemplate = document.getElementById("messageTemplate");

renderFeaturedListings();
seedConversation();

document.querySelectorAll(".quick-action").forEach((button) => {
  button.addEventListener("click", () => {
    chatInput.value = button.dataset.prompt;
    chatForm.requestSubmit();
  });
});

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = chatInput.value.trim();

  if (!text) {
    return;
  }

  appendMessage("user", escapeHtml(text));
  chatInput.value = "";

  const response = generateAssistantReply(text);
  window.setTimeout(() => {
    appendMessage("assistant", response.html);
  }, 260);
});

function seedConversation() {
  appendMessage(
    "assistant",
    [
      "Welcome to <strong>M.Residence</strong>. I can help you explore homes in Cyprus, narrow down the right fit, and line up a viewing.",
      "To get started, are you mainly looking for an apartment, house, or villa, and which area is top of mind?"
    ].join("\n\n")
  );
}

function renderFeaturedListings() {
  featuredListings.innerHTML = listings
    .slice(0, 3)
    .map(
      (listing) => `
        <article class="listing-card">
          <div class="listing-top">
            <div>
              <h3>${listing.title}</h3>
              <p class="listing-meta">${listing.type} | ${listing.bedrooms} bedrooms | ${listing.location}</p>
            </div>
            <div class="listing-price">${listing.priceLabel}</div>
          </div>
          <p class="listing-copy">${listing.blurb}</p>
          <div class="listing-tags">
            ${listing.tags.map((tag) => `<span class="listing-tag">${tag}</span>`).join("")}
          </div>
        </article>
      `
    )
    .join("");
}

function appendMessage(role, html) {
  const fragment = messageTemplate.content.cloneNode(true);
  const node = fragment.querySelector(".message");
  const bubble = fragment.querySelector(".bubble");
  node.classList.add(role);
  bubble.innerHTML = html;
  chatThread.appendChild(fragment);
  chatThread.scrollTop = chatThread.scrollHeight;
}

function generateAssistantReply(input) {
  const normalized = input.toLowerCase();

  extractPreferences(normalized);

  if (tryBookSpecificSlot(normalized)) {
    return {
      html: [
        `Perfect, I have penciled you in for <strong>${leadProfile.viewingBooked}</strong>.`,
        `I will note your interest in <strong>${leadProfile.selectedListing || "the shortlisted property"}</strong>. Before the viewing, would you like me to suggest one or two comparable options so you can compare value on the same trip?`
      ].join("\n\n")
    };
  }

  if (mentionsBooking(normalized)) {
    const shortlist = getRecommendedListings();
    const selected = shortlist[0];
    if (selected) {
      leadProfile.selectedListing = selected.title;
    }

    return {
      html: [
        `Absolutely. ${selected ? `The strongest fit so far is <strong>${selected.title}</strong> at <strong>${selected.priceLabel}</strong>.` : "I can arrange that for you."}`,
        "Here are a few viewing times available this week:",
        renderSlots(viewingSlots),
        "If one works, reply with the time and I will confirm it for you."
      ].join("\n\n")
    };
  }

  if (asksForSimilar(normalized) || asksForRecommendations(normalized)) {
    const matches = getRecommendedListings();
    return {
      html: buildRecommendationReply(matches, true)
    };
  }

  if (asksAboutProperties(normalized) || mentionsLocationOrBudget(normalized)) {
    const matches = getRecommendedListings();
    const missing = getMissingQualifiers();
    const followUp = missing.length
      ? `To refine this properly, could you also share your ${missing.slice(0, 2).join(" and ")}?`
      : "Would you like me to line up a viewing or show you a couple of comparable alternatives in the same bracket?";

    return {
      html: `${buildRecommendationReply(matches, false)}\n\n${followUp}`
    };
  }

  return {
    html: buildNaturalFallback()
  };
}

function extractPreferences(normalized) {
  const budgetMatch = normalized.match(/(?:eur)?\s?(\d+(?:[\.,]\d+)?)\s?(k|m|million)?/i);
  if (budgetMatch) {
    const raw = Number.parseFloat(budgetMatch[1].replace(",", "."));
    const multiplier = budgetMatch[2] === "m" || budgetMatch[2] === "million" ? 1000000 : budgetMatch[2] === "k" ? 1000 : raw < 10 ? 100000 : 1;
    const parsedBudget = Math.round(raw * multiplier);
    if (parsedBudget >= 50000) {
      leadProfile.budget = parsedBudget;
    }
  }

  const bedroomMatch = normalized.match(/(\d)\s*bed/);
  if (bedroomMatch) {
    leadProfile.bedrooms = Number.parseInt(bedroomMatch[1], 10);
  }

  const knownLocations = ["strovolos", "lakatamia", "limassol", "engomi", "aglantzia", "archangelos", "nicosia"];
  const foundLocation = knownLocations.find((location) => normalized.includes(location));
  if (foundLocation) {
    leadProfile.location = capitalize(foundLocation);
  }

  if (normalized.includes("apartment")) {
    leadProfile.purpose = "Apartment";
  } else if (normalized.includes("house")) {
    leadProfile.purpose = "House";
  } else if (normalized.includes("villa")) {
    leadProfile.purpose = "Villa";
  }

  const timelineSignals = ["this month", "next month", "asap", "soon", "3 months", "six months", "investment"];
  const foundTimeline = timelineSignals.find((signal) => normalized.includes(signal));
  if (foundTimeline) {
    leadProfile.timeline = foundTimeline;
  }
}

function getRecommendedListings() {
  const scored = listings
    .map((listing) => ({
      listing,
      score: getListingScore(listing)
    }))
    .sort((a, b) => b.score - a.score || a.listing.price - b.listing.price)
    .map((item) => item.listing);

  return scored.slice(0, 3);
}

function getListingScore(listing) {
  let score = 0;

  if (leadProfile.location) {
    if (listing.location === leadProfile.location) {
      score += 4;
    } else if (leadProfile.location === "Nicosia" && listing.location !== "Limassol") {
      score += 2;
    }
  }

  if (leadProfile.budget) {
    const delta = Math.abs(listing.price - leadProfile.budget);
    if (delta <= leadProfile.budget * 0.08) {
      score += 4;
    } else if (delta <= leadProfile.budget * 0.2) {
      score += 2;
    }
  }

  if (leadProfile.bedrooms) {
    if (listing.bedrooms === leadProfile.bedrooms) {
      score += 3;
    } else if (Math.abs(listing.bedrooms - leadProfile.bedrooms) === 1) {
      score += 1;
    }
  }

  if (leadProfile.purpose && listing.type.toLowerCase().includes(leadProfile.purpose.toLowerCase())) {
    score += 3;
  }

  return score;
}

function buildRecommendationReply(matches, directAnswer) {
  const intro = directAnswer
    ? "Here are the closest matches I would suggest based on what you have shared:"
    : "Based on your brief, these are the properties I would put forward first:";

  if (!matches.length) {
    return "I can help with that. If you share your preferred area, budget, and ideal number of bedrooms, I will narrow the shortlist immediately.";
  }

  leadProfile.selectedListing = matches[0].title;

  return [
    intro,
    renderMiniListings(matches),
    "From a buyer-fit perspective, the first option is the strongest starting point, and the next two give you good alternatives on price or location."
  ].join("\n\n");
}

function buildNaturalFallback() {
  const missing = getMissingQualifiers();
  const prompt = missing.length
    ? `A quick way for me to narrow it down is your ${missing.slice(0, 3).join(", ")}.`
    : "I already have enough to start matching options.";

  return [
    "I can help with search, comparisons, or a viewing arrangement.",
    prompt,
    "For example, you can say: <strong>I want a 3 bedroom house in Lakatamia around EUR400,000 and I would like to move within 3 months.</strong>"
  ].join("\n\n");
}

function getMissingQualifiers() {
  const missing = [];
  if (!leadProfile.budget) missing.push("budget");
  if (!leadProfile.location) missing.push("preferred location");
  if (!leadProfile.timeline) missing.push("timeline");
  return missing;
}

function renderMiniListings(matches) {
  return `
    <div class="mini-listings">
      ${matches
        .map(
          (listing) => `
            <div class="mini-card">
              <div class="mini-card-title">${listing.title} | ${listing.priceLabel}</div>
              <div class="mini-card-meta">${listing.bedrooms} bedrooms | ${listing.location} | ${listing.blurb}</div>
            </div>
          `
        )
        .join("")}
    </div>
  `;
}

function renderSlots(slots) {
  return `
    <div class="slot-row">
      ${slots.map((slot) => `<span class="slot">${slot}</span>`).join("")}
    </div>
  `;
}

function mentionsBooking(normalized) {
  return ["book", "viewing", "visit", "schedule", "calendar"].some((term) => normalized.includes(term));
}

function asksForRecommendations(normalized) {
  return ["recommend", "suggest", "best option"].some((term) => normalized.includes(term));
}

function asksForSimilar(normalized) {
  return ["similar", "comparable", "alternatives"].some((term) => normalized.includes(term));
}

function asksAboutProperties(normalized) {
  return ["property", "properties", "apartment", "house", "villa", "home", "listing", "listings"].some((term) => normalized.includes(term));
}

function mentionsLocationOrBudget(normalized) {
  return !!leadProfile.location || !!leadProfile.budget || !!leadProfile.bedrooms;
}

function tryBookSpecificSlot(normalized) {
  const slot = viewingSlots.find((item) => normalized.includes(item.toLowerCase()));
  if (!slot) {
    return false;
  }

  leadProfile.viewingBooked = slot;
  return true;
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
