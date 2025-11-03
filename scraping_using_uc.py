import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
import json


# Path to the Excel file
file_path = './ScrapingSezane.xlsx'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SITE_CONFIG is a single, site-specific dictionary you should edit
# before running the script for a different site.
SITE_CONFIG = {
    'selectors': {
        'products': 'a.c-card__link.u-flex-item-fluid',
        'product_link': None,
        'product_json_attr': 'onclick',
        'cookie_button': 'button.onetrust-close-btn-handler.banner-close-button.ot-close-link',
        'see_all_button': 'button.btn.btn-outline-primary.more.plp-action-btn',
        'more_button': 'a.btn.btn-primary.more.plp-action-btn'
    },
    'json': {
        'onclick_strip': {'start': 32, 'end': -1}
    },
    'mapping': {
        'product_name': 'productName',
        'product_price': 'productPrice',
        'product_ean': 'productEAN',
        'product_cat': 'productCategory',
        'product_color': 'color',
        'product_variant': 'productVariant',
        'product_collection': 'collection',
        'product_ID': 'productID'
    },
    'output': {
        'excel_dir': os.path.join(BASE_DIR, 'fichiers excel')
    },
    'wait_times': {
        'initial': 3,
        'between_clicks': 3
    }
}

def run_scrap(url, brand_name, category):
    try:
        # Launch browser and open URL
        chrome_options = uc.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        driver = uc.Chrome(options=chrome_options)
        driver.get(url)

        # Wait for the page to load (configurable)
        initial_wait = SITE_CONFIG['wait_times']['initial']
        time.sleep(initial_wait)

        # Dismiss cookie banner if configured
        click_continue_without_accepting(driver)

        # Click the "See all" button if available, otherwise try to load more
        if not click_seeall_button(driver):
            load_all_products(driver)

        # Wait until products are visible (selector comes from SITE_CONFIG)
        products_selector = SITE_CONFIG['selectors']['products']
        products = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, products_selector))
        )

        print(f"Number of products found: {len(products)}")

        # Extracting data
        data = []
        for product in products:
            try:
                selectors = SITE_CONFIG['selectors']

                # Product URL: either from a sub-link or the element's href
                product_link_selector = selectors['product_link']
                if product_link_selector:
                    try:
                        link_el = product.find_element(By.CSS_SELECTOR, product_link_selector)
                        product_href = link_el.get_attribute('href')
                    except Exception:
                        product_href = None
                else:
                    product_href = product.get_attribute('href')

                # Get raw JSON-like data from configured attribute
                json_attr = selectors['product_json_attr']
                parsed = {}
                if json_attr:
                    raw = None
                    try:
                        raw = product.get_attribute(json_attr)
                    except Exception:
                        raw = None

                    if raw:
                        strip_cfg = SITE_CONFIG['json']['onclick_strip']
                        try:
                            if strip_cfg and isinstance(strip_cfg, dict) and strip_cfg.get('start') is not None:
                                start = strip_cfg.get('start', 0)
                                end = strip_cfg.get('end', None)
                                raw_json = raw[start:end] if end is not None else raw[start:]
                            else:
                                raw_json = raw
                            parsed = json.loads(raw_json)
                        except Exception:
                            parsed = {}

                # Build product data from mapping
                mapping = SITE_CONFIG['mapping']
                product_data = {}
                for out_field, src in mapping.items():
                    try:
                        if not isinstance(src, str):
                            raise TypeError(f"Mapping for {out_field} must be a string key.")
                        product_data[out_field] = parsed.get(src) if isinstance(parsed, dict) else None
                    except Exception:
                        product_data[out_field] = None

                product_data['product_URL'] = product_href

                if product_data not in data:
                    data.append(product_data)
            except Exception as e:
                print(f"Error extracting one product: {e}")

        if not data:
            print("No data to save.")
        else:
            df = pd.DataFrame(data)

            # Save the data to an Excel sheet (output dir from SITE_CONFIG)
            output_dir = SITE_CONFIG['output']['excel_dir']
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"{brand_name}.xlsx")
            if os.path.exists(file_path):
                with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name=category, index=False)
            else:
                with pd.ExcelWriter(file_path, mode='w', engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=category, index=False)

            print(f"Finished extracting products for category '{category}' and saved to {file_path}.")
    finally:
        driver.quit()


def click_continue_without_accepting(driver):
    try:
        # Use cookie selector from SITE_CONFIG if present
        cookie_selector = SITE_CONFIG['selectors']['cookie_button']
        if not cookie_selector:
            return
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cookie_selector))).click()
        print("Cookie banner dismissed.")
    except Exception:
        print("Cookie banner not found or already dismissed.")



def click_seeall_button(driver):
    try:
        # Use 'see all' selector from SITE_CONFIG
        see_all_selector = SITE_CONFIG['selectors']['see_all_button']
        if not see_all_selector:
            return False
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, see_all_selector))).click()
        print("Clicked 'See all' button.")
        time.sleep(SITE_CONFIG['wait_times']['between_clicks'])
        return True
    except Exception as e:
        print("'See all' button not found or already clicked.")
        return False



def load_all_products(driver):
    while True:
        try:
            # Use 'more' selector from SITE_CONFIG
            more_selector = SITE_CONFIG['selectors']['more_button']
            if not more_selector:
                return
            more_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, more_selector)))
            more_button.click()
            print("Clicked 'More products'.")
            time.sleep(SITE_CONFIG['wait_times']['between_clicks'])
        except Exception as e:
            print("All products loaded or 'more' button not found.")
            break



def scroll_to_bottom(driver):
    """Scroll to the bottom to load all products."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# Example usage
if __name__ == "__main__":
    run_scrap("https://www.sezane.com/fr/collection/robes",
              "Sezane", "Robe")
    run_scrap("https://www.sezane.com/fr/collection/bas/pantalons",
              "Sezane", "Pantalon")

