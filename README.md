# news-image-20261124 — The World in One Day

A make.fun entry for **news-image-20261124**: "Sum up 24 November's world news
in one image."

`main.py` (Python 3.13, standard library only) draws a 1024x1024
newspaper-style infographic and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output/entry.png`). It runs with no network and is fully
deterministic: two runs produce byte-identical output.

## The day: Tuesday 24 November 2026

Seven stories, each verified as having happened, or first been reported,
on 24 November 2026 (sources: Reuters, AP, Xinhua, gov.uk):

1. **Lukashenko offers to fly with Zelenskyy to Moscow** — Belarus leader
   says he would guarantee Zelenskyy's safety at Kremlin talks; Zelenskyy
   answers: bring Putin to Kyiv instead.
2. **Russian strike hits Zaporizhzhia** — overnight attack on homes kills 2
   and wounds 40, including 4 children.
3. **Israeli strikes kill 6 in Gaza** — strikes hit Khan Younis and the
   Netzarim corridor despite the October 2025 ceasefire.
4. **Britain sanctions the Houthis** — asset freeze on Ansar Allah and 4
   senior officials over abuses and Red Sea attacks.
5. **China unveils the Shenzhou-24 crew** — Pakistani pilot Muhammad Zeeshan
   Ali is the first foreign astronaut to visit Tiangong. Launch set for
   Wednesday (25 Nov) — the 24 Nov event is the crew unveiling.
6. **Hanoi hot pot blast kills 6** — suspected gas leak levels a hot pot
   eatery in Dong Da; more than a dozen hurt.
7. **Teen held after school shooting in Serbia** — a 17-year-old fired a
   rifle at a technical school in Kragujevac; two staff hurt.

## How it is drawn

The program renders everything in code: a masthead naming the day
("24 NOVEMBER 2026"), a lead story, and six story cards, each with a
region tag, a headline, a one-line fact, and a small pictogram (plane,
blast, building, document, rocket, flame, schoolhouse). Text uses a 5x7
bitmap font defined in the program, so no font files or network are needed.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Verification

- Two runs produce identical bytes (same sha256).
- Output: 1024x1024 PNG, 22,278 bytes (limit: 1 MiB).

## License

MIT — see LICENSE.
