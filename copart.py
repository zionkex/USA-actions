import asyncio
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import re
from selenium.webdriver.chrome.options import Options

def scrape_copart_page(url: str):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-burl-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(8)
        
        page_html = driver.page_source
        with open("saved_page.html", "w", encoding="utf-8") as f:
            f.write(page_html)  # Wait for the page to load

        details = {
            "🚗 Назва авто": "Не знайдено",
            "📄 Документи": "Не знайдено",
            "📅 Рік": "Не знайдено",
            "📏 Пробіг": "Не знайдено",
            "⚙️ Привід": "Не знайдено",
            "⛽ Тип палива": "Не знайдено",
            "🛠️ Двигун": "Не знайдено",
            "📍 Локація": "Не знайдено",
            "🌟 Стан авто": "Не знайдено",
        }

    
        try:
            car_name_element = driver.find_element(By.CLASS_NAME, "title.my-0.mr-10")
            details["🚗 Назва авто"] = car_name_element.text
        except:
            pass

        try:
            title_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Title code')]/following-sibling::span")
            details["📄 Документи"] = title_element.text.strip()
        except:
            pass

        if details["🚗 Назва авто"]:
            year_match = re.search(r'\b(19|20)\d{2}\b', details["🚗 Назва авто"])
            if year_match:
                details["📅 Рік"] = year_match.group(0)

        try:
            odometer_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Odometer')]/following-sibling::*")
            details["📏 Пробіг"] = odometer_element.text
        except:
            pass

        try:
            drive_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Drive')]/following-sibling::*")
            details["⚙️ Привід"] = drive_element.text
        except:
            pass

        try:
            fuel_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Fuel')]/following-sibling::*")
            details["⛽ Тип палива"] = fuel_element.text
        except:
            pass

        try:
            engine_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Engine type')]/following-sibling::*")
            engine_text = engine_element.text.strip()
            details["🛠️ Двигун"] = engine_text  # Зберігаємо тільки текст двигуна
            
            # Регулярний вираз для пошуку першого числа у форматі 2.5 або 2,5
            match = re.search(r"(\d+[.,]\d+)", engine_text)
            
            if match:
                try:
                    engine_volume = float(match.group(1).replace(",", ".")) * 1000
                except ValueError:
                    pass
        except Exception as e:
            print(f"Помилка при отриманні інформації про двигун: {str(e)}")
            pass

        try:
            sale_location_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Sale location')]/following-sibling::*")
            details["📍 Локація"] = sale_location_element.text
        except:
            pass

        try:
            highlights_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Highlights')]/following-sibling::*")
            details["🌟 Стан авто"] = highlights_element.text
        except:
            pass

        return details
    except Exception as e:
        return {"error": f"❌ Помилка: {str(e)}"}
    finally:
        driver.quit()


async def fetch_car_info_copart(url):
    loop = asyncio.get_running_loop()
    details = await loop.run_in_executor(None, scrape_copart_page, url)
    return details