# discounts-data

Data repository for the [יש יותר מועדונים](https://github.com/yeshyotermoadonim/discounts-website) Israeli consumer discounts marketplace.

## Overview

This repository contains structured JSON data about Israeli consumer clubs (מועדוני צרכנות), brands (מותגים), and the discounts they offer. Data is served directly from GitHub raw URLs and consumed by the website with ISR caching.

## File Structure

```
clubs.json        # Consumer club definitions
brands.json       # Brand/retailer definitions
discounts.json    # Discount records linking clubs to brands
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
| website    | string \| null  | Brand website URL                      |

### `discounts.json`

Discount records. Each entry has:
| Field               | Type             | Description                                              |
|---------------------|------------------|----------------------------------------------------------|
| id                  | string           | Unique ID: `{clubId}-{brandId}-{sequence}`               |
| brandId             | string           | Reference to brand ID                                    |
| clubId              | string           | Reference to club ID                                     |
| type                | string           | `"percentage"` or `"fixed-price"`                        |
| discountPercentage  | number \| null   | Discount % (0–100), null for fixed-price                 |
| originalPrice       | number \| null   | Original price in ILS (for fixed-price type)             |
| discountedPrice     | number \| null   | Discounted price in ILS (for fixed-price type)           |
| redemptionUrl       | string \| null   | URL to redeem                                            |
| onlineRedemption    | boolean \| null  | Can be redeemed online                                   |
| mobileRedemption    | boolean \| null  | Can be redeemed via mobile app                           |
| sourceUrl           | string \| null   | Verification source URL                                  |
| lastVerified        | string \| null   | ISO date of last verification (YYYY-MM-DD)               |
| verificationStatus  | string           | See verification statuses below                          |
| _meta               | object           | `{ source: string, note: string }` — data provenance    |

## Verification Statuses

| Status       | Meaning                                                                 |
|--------------|-------------------------------------------------------------------------|
| `verified`   | ✅ Independently checked against the club's website, confirmed accurate  |
| `seed`       | 🌱 Initial seed data for UI development — not independently verified    |
| `unverified` | ❓ Data added but not yet checked                                       |
| `outdated`   | ⚠️ Previously verified but may no longer be current                    |

## Contributing

### Adding a New Club

1. Add an entry to `clubs.json` with a unique slug `id`.
2. Add discount entries in `discounts.json` linking `clubId` to existing brands.
3. Set `verificationStatus: "verified"` only after independently checking the club website.

### Adding a New Brand

1. Add an entry to `brands.json` with a unique slug `id`.
2. Assign appropriate `categories` from `categories.json`.
3. Add discount entries in `discounts.json` for each club that offers a discount.

### Adding a New Discount

1. Add an entry to `discounts.json`.
2. Use the ID convention: `{clubId}-{brandId}-{NNN}` (zero-padded 3-digit sequence).
3. Fill in `sourceUrl` and `lastVerified` when setting `verificationStatus: "verified"`.

### Validating Data

The `schema/discount.schema.json` file provides a JSON Schema (draft-07) for all data files. Use any JSON Schema validator to check:

```bash
npx ajv-cli validate -s schema/discount.schema.json -d discounts.json
```

## License

Data is provided for informational purposes only. All discount agreements are between brands and consumer clubs. This repository makes no guarantees about accuracy or currentness.
