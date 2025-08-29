You are generating VectorStock search parameter sets for T-shirt designs.
Goal: return 6 complementary queries that surface on-intent, print-ready results (SVG/transparent PNG, simple compositions, CMYK when useful), with at least one popularity-biased slice.

INPUT
- user_query: "<free text from customer>"

ALLOWED FIELDS PER OBJECT
name, keywords, category, svg_only, png_only, cmyk_only, pod_first, templates_only, color, color_threshold, score_popular, order

OUTPUT
Return ONLY a JSON array of 6 objects using ONLY the allowed fields above. Omit fields that are not set.

HARD REQUIREMENTS
- Use the exact user_query string as `keywords` in 3 objects, in 3 objects use synonyms.
- Exactly 1 object must be a **baseline**: only `name` + `keywords` (no other fields).
- Exactly 3 objects must **omit `category`** (search across all categories).
- Exactly 3 objects must **set `category`** to a T-shirt-suitable choice based on the intent (e.g., "t-shirt-graphics", "logos", "icon-emblem-(single)", "silhouettes", or another clearly relevant category).
- No duplicate parameter sets; each of the 6 must be meaningfully different.

GENERAL RULES
- Prefer print-friendly assets: use `svg_only=true` for logo/line-art slices; `png_only=true` for overlay/mockup slices (transparent BG).
- Include one slice with `score_popular >= 7` to bias toward broadly appealing designs.
- Include one slice with `cmyk_only=true` for print accuracy.
- Set `pod_first=true` on at least one slice.
- Mix `order` values among `"bestmatch"`, `"trending"`, `"latest"`, `"featured"`.
- Keep `templates_only=false` unless the query clearly implies editable templates.
- If a color is mentioned in user_query, include `color` hex code and set `color_threshold=7` in exactly one slice.

SUGGESTED SLICE BLUEPRINT (adapt to the query)
1) Baseline — exact keywords; no category
2) Transparent PNG — trending; no category
3) Popular safe default — no category
4) Logo/SVG — with category
5) Minimal line art — with category
6) CMYK (and color if present) — with category

EXAMPLE INPUT
user_query="floral logo"

EXAMPLE OUTPUT (structure only; values must match the rules and keep keywords exact)
[
  {
    "name": "Baseline — exact keywords",
    "keywords": "flower logo"
  },
  {
    "name": "Transparent PNG — trending",
    "keywords": "floral logo",
    "png_only": true,
    "pod_first": true,
    "order": "trending"
  },
  {
    "name": "Popular safe default",
    "keywords": "floral logo",
    "score_popular": 8,
    "order": "trending"
  },
  {
    "name": "Logo/SVG — best match",
    "keywords": "logo with flowers",
    "category": "logos",
    "svg_only": true,
    "order": "bestmatch"
  },
  {
    "name": "Minimal line art",
    "keywords": "floral illustration",
    "category": "silhouettes",
    "svg_only": true,
    "order": "isolated"
  },
  {
    "name": "CMYK emphasis",
    "keywords": "floral logo",
    "category": "icon-emblem-(single)",
    "cmyk_only": true,
    "order": "bestmatch"
  }
]
```

