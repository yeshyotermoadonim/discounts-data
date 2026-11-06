# discounts-data

Data repository for the [יש יותר מועדונים](https://github.com/yeshyotermoadonim/discounts-website) Israeli consumer discounts marketplace.

## Overview

This repository contains structured JSON data about Israeli consumer clubs (מועדוני צרכנות), brands (מותגים), and the discounts they offer. Data is served directly from GitHub raw URLs and consumed by the website with ISR caching.

## File Structure

```
clubs.json        # Consumer club definitions
brands.json       # Brand/retailer definitions
listings.json     # Where each brand is available, per club
categories.json   # Product category taxonomy
schema/
  discount.schema.json  # JSON Schema (draft-07) for all data files
```

## Data Files

### `categories.json`

Product category taxonomy. Each entry has:
| Field | Type   | Description              |
|-------|--------|--------------------------|
| id    | string | Unique slug (e.g. `beauty`) |
| name  | string | Hebrew display name      |

### `clubs.json`

Consumer club definitions. Each entry has:
| Field  | Type    | Description                        |
|--------|---------|------------------------------------|
| id     | string  | Unique slug (e.g. `hever-sheli`)   |
| name   | string  | Hebrew display name                |
| nameEn | string  | English display name               |
| url    | string  | Club homepage URL                  |
| color  | string  | Brand color as hex (e.g. `#0057B7`) |
| active | boolean | Whether the club is currently active |

### `brands.json`

Brand/retailer definitions. Each entry has:
| Field      | Type            | Description                            |
|------------|-----------------|----------------------------------------|
| id         | string          | Unique slug (e.g. `careline`)          |
| name       | string          | Display name                           |
| categories | string[]        | Array of category IDs                  |
| logoUrl    | string \| null  | Logo image URL                         |

### `listings.json`

One row per brand per club. A row means the brand is available there. These club pages do not publish a percentage, so none is stored. `online` belongs to that club listing: the same brand can be online in one club and not in another.

| Field   | Type    | Description                                      |
|---------|---------|--------------------------------------------------|
| brandId | string  | Reference to brand ID                            |
| clubId  | string  | Reference to club ID                             |
| online  | boolean | Redeemable online in this club                   |
| url     | string  | Club page for this brand                         |

## Updating

Put the three saved pages in one folder as `Beazdaa.html`, `Hever.html`, and `BuyMe.html`, then:

```bash
./scripts/update.sh ~/Downloads/Moadonim/2026-11-6
```

That rewrites `clubs.json`, `brands.json`, `categories.json`, and `listings.json`, and copies them into the website seed. Commit and push this repo. The website reads the raw GitHub files and refreshes within about an hour. It does not redeploy Vercel. Design changes are deployed from `discounts-website` with `./scripts/deploy.sh`.

Saved club pages can also be rebuilt directly:

```bash
python3 scripts/build_dataset.py
python3 scripts/parse_behatsdaa.py --limit 5
```

### Adding a listing

1. Add the brand to `brands.json` if it is new.
2. Add one object to `listings.json` with `brandId`, `clubId`, `online`, and `url`.
3. Do not invent a percentage. Availability is the record.

### Validating Data

```bash
npx ajv-cli validate -s schema/discount.schema.json -d listings.json
```

## License

Data is provided for informational purposes only. All discount agreements are between brands and consumer clubs. This repository makes no guarantees about accuracy or currentness.
