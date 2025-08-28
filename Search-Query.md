# Search API
- https://api.vectorstock.com/p1/search

| Name | Data Type | Description | Default Value | Available Values |
|------|-----------|-------------|---------------|------------------|
| **keywords** * | string | Search term | - | - |
| **category** | string | Category | - | abstract, animals-wildlife, artistic-experimental, backgrounds-textures, beauty-fashion, borders-frames, buildings-landmarks, business-finance, cartoons, celebration-party, children-family, christmas, cityscapes, communication, computers, copy-space, dj-dance-music, dancing, design-elements, digital-media, document-template, easter, education, entertainment, flags-ribbons, floral-decorative, fonts-type, food-drink, game-assets, geographical-maps, graffiti, graphs-charts, grunge, halloween, healthcare-medical, heraldry, housing, icon-emblem-(single), icons-emblems-(sets), industrial, infographics, interiors, landscapes-nature, logos, military, miscellaneous, music, objects-still-life, packaging, patterns-(seamless), patterns-(single), people, photo-real, religion, science, seasons, shopping-retail, signs-symbols, silhouettes, sports-recreation, t-shirt-graphics, technology, telecommunications, transportation, urban-scenes, user-interface, vacation-travel, valentines-day, vintage, weddings |
| **artist** | string | Artist name | - | - |
| **page** | integer($int32) | The page number to be used for scrolling | - | - |
| **free** | boolean | Search free vectors only | false | - |
| **expanded** | boolean | Expanded license vectors only | false | - |
| **object_detection** | string | Show vector images with white borders and distinct objects | false | show_objects, hide_objects |
| **object_count_min** | integer($int32) | A range from 1 to 200 for minimum distinct objects | - | - |
| **object_count_max** | integer($int32) | A range from 1 to 200 for maximum distinct objects | - | - |
| **svg_only** | boolean | Search vector images with SVG files only | false | - |
| **templates_only** | boolean | Search template vector images only | false | - |
| **pod_first** | boolean | Show Print-On-Demand vector images first in results | false | - |
| **cmyk_only** | boolean | Search vector images using CMYK color model only | false | - |
| **png_only** | boolean | Search vector images with transparent PNG files only and order based on transparency | false | - |
| **editorial** | boolean | Include vector images with editorial licenses in the search results | false | - |
| **count_only** | boolean | Only return the number of search results, exclude the actual results | false | - |
| **color** | string | A color in hexadecimal color code format for searching only vector images that have predominantly this color | - | - |
| **color_threshold** | integer($int32) | A range from 1 to 10 for how much color filtering to apply | - | - |
| **score_popular** | integer($int32) | A range from 1 to 10 for filtering by artwork popularity | - | - |
| **artist_score** | integer($int32) | A range from 1 to 10 for filtering by artist score ranking | - | - |
| **order** | string | Search results sort order | - | trending, bestmatch, latest, isolated, featured |

\* Required parameter

