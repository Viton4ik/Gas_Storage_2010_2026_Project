# Who Stores the Most Gas? 2010–2026

Final project: 120 seconds, 1080 × 1920, 60 fps. English on-screen text.
Read REVIEW.md for definitions, changing country coverage and source cautions.

The leader is pinned above six racing rows. One bottom row selects the lowest
strictly positive reported month-end stock among all eligible reporters.
The chosen country can change each month. Zeros and missing data are excluded.
Up to seven decimal places keep small positive values from appearing as zero.

All main-race bar geometry, backgrounds, fonts and flags use the unchanged
reference CO₂ render.py. render_storage.py provides the source-based positive
minimum, more precise lower values, overall rank labels and adaptive timeline.
The palette is steel blue; the original generated soundtrack is D minor,
112 BPM, seed 201026.

## Reproduce

Requires Python 3, ffmpeg, and requirements.txt packages. Included fonts and
flags do not require downloading again. From this project directory:

```sh
python scripts/build_data.py
python scripts/render_video.py --workers 4
```

This regenerates data, checks ranking, renders via engine/render_storage.py,
creates the 120-second music track and masters/muxes the final MP4. The path is
set by config.json. Do not use the generic render.py entry point for the final
film, because the specialized positive-minimum and timing rules are in the
wrapper.

## Timeline

2 s intro + 111.4 s race + 1.6 s final hold + 5 s outro. More time is allocated
to 2011, 2013 and 2021; all 200 source months remain in the monotone time map.
Three 0.25-second holds let the rows settle at December 2011, 2013 and 2021.

## Files

- REVIEW.md: data provenance, confidence flags and methodology.
- data/assessed_reported_stocks.csv: eligible raw monthly levels and flags.
- data/monthly_positive_minimum.csv: all 200 monthly winners and ties.
- data/values.csv: renderer input with non-overlapping missing-data spans.
- data/raw/: unchanged downloaded JODI publication CSV and source metadata.
- config.json, scripts/, engine/, assets/: complete reproduction components.
- validation/: ranking, minimum-selection, media and loudness checks.
- YOUTUBE_DESCRIPTION.md: titles, description, source links and limitations.

The minimum is among the reporting countries retained by the stated screening
policy. This is not a complete world ranking. This measures gas inventories,
not geological reserves, storage capacity or a separately defined state reserve.
