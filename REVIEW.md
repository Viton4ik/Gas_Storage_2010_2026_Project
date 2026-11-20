# Gas in storage: data and visual review

Status: final 120-second video project.

## Scope and metric

January 2010 through August 2026, 200 monthly observations per complete series.
Metric: reported recoverable gas stocks on national territory at month end,
in billion standard cubic metres (15°C, 760 mm Hg). Source values in million
cubic metres are divided by 1,000. Stocks may include gaseous and regasified
LNG inventories. This is not storage capacity, geological reserves, or a
separately identified government strategic reserve.

Source: JODI-Gas, publication 28, downloaded 18 November 2026:
https://www.jodidata.org/jodi-publisher/gas/28/GAS_world_NewFormat.zip

Definitions:
https://www.jodidata.org/gas/support/user-guide/data-available-in-the-jodi-gas-world-database.aspx

Assessment-code definitions:
https://www.jodidata.org/_resources/files/downloads/gas-data/jodi-gas-wdb-short--long-names-ver2025.pdf

## Screening and limitations

- Code 1: assessment indicates reasonable comparability with other sources.
- Code 2: consult metadata/use with caution. These official reported figures
  are retained as caution observations, not promoted to code 1.
- Code 3: not assessed. These observations are excluded from this review.
- Canada in August 2026 is code 2; it is 25.793 billion m³. The visible label
  Canada* and footnote identify this qualification. Its cause has not been
  resolved, so final data acceptance remains a review decision.
- Russia's entire available stock series is code 3 and is excluded. China has
  no matching closing-stock series in this extract. The video must not be
  described as a complete world ranking.
- Coverage changes over time. Germany starts in January 2013, Netherlands in
  January 2014, Canada in January 2016. Ukraine's series ends in January 2022.
  An entry/exit indicates reporting coverage, not gas appearing/disappearing.
- Genuine missing observations are never replaced by zero or carried forward.
  Interpolation animates movement between reported adjacent monthly points.
  Different national reporting practices may still affect comparability.
- August 2026 is the last broadly shared month in publication 28. September
  2026 contains only one matching stock reporter and is excluded.

## Pinned leader and monthly positive minimum

The largest eligible reporter is pinned at the top. Six main rows move in
rank order. The bottom row shows the country with the smallest strictly
positive reported stock for the displayed calendar month, selected from ALL
eligible reporters, not from a hand-picked comparison pair.

The lower label is "SMALLEST NON-ZERO STOCK · COMPARISON". Zeros, missing
reports and unassessed code-3 observations cannot win this slot. If multiple
countries share the same positive minimum, the current country stays when
still tied; otherwise the alphabetically first country code is used.

The lower value is the exact reported month-end observation, displayed with
up to seven decimal places in billion m³, with trailing zeros removed. Its
monthly report is not replaced by an interpolated between-month minimum.
The main race continues to use interpolated motion. All monthly winners,
ties and assessment codes are saved in data/monthly_positive_minimum.csv.
Code-2 winners are marked with an asterisk and a caution footnote.

A name change uses the original slot crossfade, shortened to 0.25 seconds.
The outgoing country briefly retains its preceding reported value during the
fade. The minimum is not duplicated among the visible main rows. Main rows
include Japan and South Korea whenever they qualify; no fixed pair is removed.

## Missing spans and the reference engine

The original CO₂ renderer file is unchanged. A small storage-specific wrapper
adds positive-minimum selection, precise numbers, time mapping and overall rank labels. All geometry,
fonts, bar rendering and spring animation remain delegated to render.py. A country with a gap is represented by
non-overlapping internal aliases, each containing a contiguous observed span.
Every alias retains the same visible name and flag. It cannot appear twice
at any monthly observation. Values outside each active span are blank.
This allows the original renderer to handle missing observations without
inventing values or changing the bar geometry.

## Style and pacing proposal

Original composition, fonts, light bar bodies and 3D geometry are retained.
The leader and one dynamically selected positive-minimum row are pinned. Subtle steel-blue palette.
New original D minor soundtrack, 112 BPM, seed 201026.

The proposed full duration is 120 seconds: 2 intro, 111.4 race, 1.6 final
hold, 5 outro. The wrapper allocates more screen time to 2011 (weight 1.25),
2013 (1.4) and 2021 (1.25). Other years have weight 1.0, then all durations
are normalized to the fixed total. A monotone time mapping preserves every
monthly observation. Three 0.25-second holds are added at December 2011,
December 2013 and December 2021. Springs continue settling during these holds.

The full-length output is 120 seconds. Source-month coverage, the lower
minimum, positivity and display precision are checked on every rendered
state. Audio and video checks are saved in validation/.

## Files

`data/assessed_reported_stocks.csv`: screened monthly factual table with
assessment codes; no interpolation or fabricated observations.
`data/summary.json`: coverage counts, key-month top tens and zero ties.
`data/values.csv`: renderer input, with separate aliases for missing spans.
`scripts/build_data.py`: reproducible screening and renderer-input builder.
`config.json`: colors, music, pinning, timing and captions.
`validation/`: visual and ranking checks.
