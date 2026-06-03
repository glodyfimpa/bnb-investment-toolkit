# Guest Templates

Generate the guest-communication messages a short-term rental needs across a
stay: booking confirmation, pre-arrival access instructions, in-home info,
check-out reminder, and review request. Italian and English.

The ready-to-fill message bodies live in `assets/guest-messages-it.md`. This file
explains when each message fires and how to fill it. Read the asset, fill the
`<placeholders>` from the apartment's facts, and hand the user clean text to paste
into Airbnb/Booking or schedule in their messaging tool.

## The message sequence

A stay has a small fixed set of touchpoints. Sending the right message at the
right time is most of good hosting; the two starred ones carry the most weight.

| ID | When | Purpose |
|---|---|---|
| T1 | At booking | Warm confirmation, set expectations, ask arrival time |
| **T2** ⭐ | T-1 day or once arrival time is known | Self check-in instructions (address, intercom, lockbox, door) |
| T3 | Morning of check-in | Short "ready, see you later" + reachability |
| **T4** ⭐ | In-home physical sheet | WiFi, house info, rules, emergency contacts |
| T5 | Morning of check-out | Check-out steps + time, keep it friendly |
| T6 | A few hours after check-out | Thank you + review request |

T2 and T4 are the ones that fail loudest if wrong: a guest who can't get in, or
who can't find the WiFi, messages you stressed. Get those two exact.

## Filling the templates

Each template has `<placeholders>`. Collect these once per apartment and reuse:

- Address, floor, how to reach the door (stairs/lift, which one)
- Intercom name/button, lockbox location and code
- Check-in / check-out times
- WiFi SSID and password
- Host contact (Airbnb messaging + phone)
- House rules (smoking, parties, pets)

A placeholder still showing `<...>` means a fact is missing — surface it, don't
send a half-filled message. Never put the live lockbox code in anything public
(the listing); it belongs only in T2, sent privately to a confirmed guest.

## Tone

Warm but concise. A guest reads these on a phone, often mid-travel. Lead with the
thing they need (the address, the code, the time), then the niceties. Apply the
user's WRITING STYLE GUIDE: no emoji walls, no exclamation pile-ups, one friendly
closing line. The existing Via Braida messages are the reference for register —
clear, kind, practical.

## Compliance note

Mentioning a one-time welcome/courtesy kit is fine. Promising a recurring service
(daily breakfast, daily cleaning, fridge restocking) in guest messages is not
just tone — for an Italian LT it edges toward CAV/B&B reclassification. Keep guest
messaging consistent with how the listing and the legal setup describe the place.
