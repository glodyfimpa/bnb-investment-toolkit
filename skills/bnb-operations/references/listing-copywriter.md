# Listing Copywriter

Write the public-facing copy for a short-term rental that is going (or already)
live: the Airbnb/Booking listing title, the description blocks, the guest-access
note, the neighborhood pitch, and the house rules. Italian first, English second.

This is NOT property evaluation. `short-term-rental-analyzer` decides whether an
apartment is worth buying (ROI, occupancy, zone economics). This writes the words
that sell nights once the apartment is yours. Different job, different output.

## Before writing: collect the facts

Good listing copy is specific. Vague copy ("cozy apartment in a great location")
converts worse than concrete copy ("3rd floor, two lifts, 8-minute walk to the
Duomo, sleeps 4 with a real double sofa bed"). Gather first:

- **Capacity and sleeping setup** — beds, sofa beds (open vs closed matters),
  max guests. This is the first thing a guest filters on.
- **Location anchors** — nearest metro/landmark with real walking times, not
  "central". Name the neighborhood.
- **What makes it different** — the one or two things a competing listing on the
  same street doesn't have (a real workspace, a quiet courtyard, fast WiFi, self
  check-in 24/7).
- **Constraints** — no smoking, no parties, check-in/out times, stairs/lift,
  pets. These belong in house rules, stated plainly.

If a fact is missing, ask for it or mark it `<...>` — don't invent amenities. A
listing that promises a dishwasher that isn't there generates one-star reviews.

## Output structure

Produce all of these, IT then EN. Keep each block scannable.

### 1. Title (max ~50 chars, the headline)
Lead with the strongest concrete hook + location. Examples of the right shape
(adapt, don't copy):
- `Bilocale luminoso a 8 min dal Duomo · self check-in`
- `Trilocale silenzioso in centro, sleeps 4 · WiFi veloce`

Avoid empty adjectives ("stupendo", "incredibile"). A number or a named landmark
out-pulls a superlative.

### 2. Description — "lo spazio"
Two or three short paragraphs. Open with the single most compelling concrete
fact, not a generality. Cover: what the space is and who it fits, the sleeping
setup (be explicit about sofa beds — "divano-letto matrimoniale" not "divano"),
the practical comforts (kitchen, workspace, AC/heating), and the feel of the
place in one honest line. Don't pad. A guest skims.

### 3. Guest access — "accesso ospiti"
How they get in, in plain steps. If there's self check-in via lockbox, say so —
it's a strong selling point for late arrivals. Derive the steps from
`guest-templates.md` (the T2 access message) so the listing and the messages
agree. Don't publish the actual lockbox code in the public listing.

### 4. Neighborhood — "il quartiere"
What's within a short walk: transport, food, sights. Real names, real times.
One short paragraph. This is where the location does the selling.

### 5. House rules — "regole della casa"
A short bullet list, stated as plain facts not scolding:
- Vietato fumare in tutto l'appartamento
- No feste o eventi
- Check-in dalle 15:00 · check-out entro le 10:00
- `<animali: sì/no>`

## Style

Apply the user's WRITING STYLE GUIDE (it's in their CLAUDE.md and applies to all
output, including listing prose):

- No banned words: skip "incredibile", "stupendo", "unico", "perfetto". Concrete
  detail does the persuading.
- No "non X ma Y" structures.
- Vary sentence length — a 20-word descriptive sentence next to a 5-word punch.
- No emojis, no em dashes, no exclamation pile-ups. One warm closing line is fine.

Honesty sells over time: an accurate listing earns better reviews than a hyped
one, and reviews are what rank you. Describe the real apartment well rather than
a better imaginary one.

## Compliance note (Italian LT)

For an Italian locazione turistica the listing should not describe services that
would reclassify it as CAV/B&B (daily breakfast, daily fridge restocking). A
one-time courtesy kit at check-in is fine to mention; a daily personal service
is not just a copy choice, it changes the legal category. See the user's gotchas
on LT vs CAV reclassification before promising recurring services.
