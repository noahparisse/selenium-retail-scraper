# Clothing e-commerce scrapers

> Lightweight, site-configurable scrapers for extracting product metadata from fashion e‑commerce websites and exporting results to Excel.

This repository contains a small set of Python scripts built on Selenium and undetected-chromedriver. The scrapers are driven by a single, global `SITE_CONFIG` (defined in `scraping_using_uc.py`) so you can adapt the scraper to another website by editing selectors and JSON mappings only — no logic changes required.

## 1 Contents

- `scraping_using_uc.py` — main, configurable scraper using Selenium + undetected-chromedriver.
- `fichiers excel/` — default directory where Excel outputs are written.

## 2 Key ideas

- Global site config: edit `SITE_CONFIG` at the top of `scraping_using_uc.py` to adapt to a new site.
- Robust parsing: JSON is read from element attributes or `onclick` wrappers with optional slicing.
- Output: each run writes/updates `<brand_name>.xlsx` in `fichiers excel/` and creates a sheet per category.

## 3 Requirements

- Python 3.8 or later
- Recommended packages (examples):

```sh
pip install undetected-chromedriver selenium pandas openpyxl
```

## 4 Configuration (`SITE_CONFIG`)

Open `scraping_using_uc.py` and edit the `SITE_CONFIG` dictionary near the top. Important keys:

- `selectors.products` — CSS selector matching a product tile element.
- `selectors.product_link` — optional CSS selector (relative to the tile) to get the product URL. Set to `None` if the tile exposes `href` directly.
- `selectors.product_json_attr` — attribute name that contains JSON data (e.g., `data-gtmga4data` or `onclick`).
- `selectors.cookie_button`, `selectors.see_all_button`, `selectors.more_button` — optional selectors for cookie/see-all/load-more actions.
- `json.onclick_strip` — optional `{ 'start': int, 'end': int }` slice to remove surrounding wrapper (used for `onclick(...)`).
- `mapping` — maps output field names (e.g. `product_name`, `product_price`) to a JSON key (string). Mapping values must be strings.
- `output.excel_dir` — directory where Excel files are written.
- `wait_times.initial` / `wait_times.between_clicks` — integer seconds used for simple waits.

Example snippet (from the file):

```py
SITE_CONFIG = {
	'selectors': {
		'products': 'div.product-tile',
		'product_link': 'a.tile-link',
		'product_json_attr': 'data-gtmga4data',
		'cookie_button': None
	},
	'json': { 'onclick_strip': None },
	'mapping': { 'product_name': 'item_name', 'product_price': 'price' },
	'output': { 'excel_dir': 'fichiers excel' },
	'wait_times': { 'initial': 3, 'between_clicks': 2 }
}
```

## 5 Running the scraper

Edit `SITE_CONFIG` as needed, then run the script. The repository includes a minimal example call under `if __name__ == '__main__'`.

```sh
python3 scraping_using_uc.py
```

Or call the main function from another script:

```py
from scraping_using_uc import run_scrap
run_scrap('https://example.com/collection', 'ExampleBrand', 'Dresses')
```

Output: the script creates/updates `fichiers excel/<brand_name>.xlsx` and writes the scraped products into a sheet named after the `category` argument.


