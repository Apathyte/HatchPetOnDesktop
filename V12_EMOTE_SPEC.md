# Dex v12 Emote Spec

This document defines the intended emotional animation arcs for Pack 1. Current balloons and pose switches are placeholders; these specs describe what the later animation work should communicate before any new sprite work starts.

## Shared Animation Principle

Pack 1 should be built from reusable animation beats rather than five unrelated one-off emotes.

Reusable beats:

- Low growl loop.
- Bark/pop reaction.
- Slow head drop.
- Disappointed sigh.
- Sit/slow blink/yawn.
- Nap/sleep settle.
- Patrol/watch stance.
- Alert acceleration.
- Look-back-to-user beat.
- Leash carry.
- Leash toss.

The goal is to combine these beats differently per trigger while keeping Dex's core demeanor: happy-go-lucky, big, strong, protective guardian. Even his judgment should still feel like Dex, not like a mean or hostile dog.

## Anti-Semantics

Global avoid list:

- Not an attack dog.
- Not panic.
- Not mean.
- Not fragile or scared.
- Not generic notification UI in dog form.
- Do not overcorrect away all silliness. Dex can be a little funny because his baseline personality is warm, loyal, and happy-go-lucky.

## Pack 1 Priority

1. Excel
2. PowerPoint
3. Terminal / guardian watch
4. CPU spike
5. Inactivity / leash reminder

## 1. Excel: Disappointed Guardian

Core read: Excel is Dex's least favorite. He is judging the spreadsheet energy, protecting the user from it, and going through a visible emotional arc rather than doing one static reaction.

Target animation:

1. Dex notices Excel and shifts into attention.
2. Low growl beat plays 2 or 3 times.
3. Bark-looking emote/pop happens once.
4. He transitions into a slow head drop.
5. He lands in a disappointed sigh.
6. He can then settle into nap/sleep if the state persists.

Reusable beats:

- Low growl loop.
- Bark/pop reaction.
- Slow head drop.
- Disappointed sigh.
- Nap/sleep settle.

Heat target: medium. The reaction should be opinionated but not aggressive.

Current placeholder:

- Sit pose with `GRROWWLL` balloon.

Notes:

- This sequence can be authored as separate beats first, then strung together once the animation pipeline supports it.
- Do not make this too serious. Dex is still a lovable guardian with a slightly ridiculous vendetta against spreadsheets.

## 2. PowerPoint: Bored To Sleep

Core read: PowerPoint drains Dex's soul. He tries to stay polite, gets bored, yawns, and gives up into nap mode.

Target animation:

1. Dex sits or settles into a bored watch.
2. Slow blink or small patience beat.
3. Head droop reuses the Excel head-drop beat where possible.
4. Yawn reuses or extends the disappointed-sigh/head-drop family.
5. He settles into nap/sleep mode if PowerPoint remains active long enough.

Reusable beats:

- Sit/slow blink.
- Slow head drop.
- Disappointed sigh or yawn variant.
- Nap/sleep settle.

Heat target: low to medium. It should feel like corporate boredom, not hostility.

Current placeholder:

- PowerPoint short duration: sit pose with `SIGH.` balloon.
- PowerPoint long duration: sleep pose with `YAAWN...` balloon.

Notes:

- This should reuse as much of the Excel animation family as possible.
- Difference from Excel: less growl/judgment, more boredom/yawn/surrender.

## 3. Terminal: Guardian Watch

Core read: Terminal is real work mode. Dex becomes alert, proud, and quietly protective while the user operates.

Target animation:

1. Dex enters patrol/watch stance.
2. Head comes up.
3. He does a calm scan or slow patrol.
4. He holds a steady guardian posture.

Reusable beats:

- Patrol/watch stance.
- Calm scan.
- Alert-but-steady movement.

Heat target: low to medium. Quiet security detail, not anxious.

Current placeholder:

- Patrol pose with `ON WATCH` balloon.

Future Pack 2 / event hook:

- Add a rare cat event during guardian/patrol moments.
- One cat or a small group of two or three cats enters the screen.
- Dex chases them away.
- The event should be manually testable.
- Later define interval/probability so it happens rarely during generic patrol or guardian watch.

Notes:

- The cat event is not part of Pack 1 implementation, but the guardian-watch animation should be compatible with it.

## 4. CPU Spike: Alert Patrol

Core read: Dex notices system heat/load. He becomes more urgent, but remains controlled.

Target animation:

1. Reuse Terminal/guardian watch as the base.
2. Add an alert beat: stop, notice, sharpen posture.
3. Patrol accelerates or becomes more purposeful.
4. End with a look-back-to-user beat, as if he is checking whether the user noticed too.

Reusable beats:

- Patrol/watch stance.
- Alert acceleration.
- Look-back-to-user beat.

Heat target: medium. Serious system warning without panic or zoomies.

Current placeholder:

- Patrol pose with 40 percent faster movement.
- No balloon by design.

Notes:

- Reuse the Terminal guardian stance as much as possible.
- Avoid faster frame cycling at first if it makes leg jank more visible.

## 5. Inactivity / Leash Reminder

Core read: Dex is the user's break accountability guardian. He should bring the leash in a way that feels loving, persistent, and physical, not like a nagging notification.

Target animation:

1. Dex runs to the edge of the screen.
2. He visually grabs the leash from off-screen, as if pulling it in from the side.
3. He runs back and forth across the screen twice with the leash.
4. He ends near the middle of the screen.
5. He sits with the leash in his mouth.
6. He tosses the leash forward, as if it hits the monitor for the user to pick up.

Reusable beats:

- Run to edge.
- Leash grab.
- Leash carry.
- Leash sit.
- Leash toss.

Heat target: medium-high persistence, but still loving.

Current placeholder:

- Leash pose with `WALK?` balloon through the test reaction.
- Legacy long-inactivity behavior still enters leash mode.

Notes:

- This should eventually be driven by a real-clock reminder class, not only passive inactivity.
- The leash toss is a key physical gag and should become the memorable payoff.
- This animation may require the most custom work in Pack 1.

## Implementation Prep

Before sprite work:

1. Define animation metadata for reusable beats.
2. Define each emote as a sequence of beats.
3. Add test triggers for each full sequence.
4. Keep placeholders until a beat can be reviewed in isolation.
5. Avoid new facial/body detail sprites until the animation pipeline can handle timing, anchors, and transitions.

Suggested data direction:

```text
reaction -> sequence of beats -> pose/frame set + duration + movement + overlay + interrupt behavior
```

Open question for later:

- Which beat should be prototyped first: Excel growl/head-drop, Terminal watch stance, or leash carry/toss?
