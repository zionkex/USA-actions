import asyncio
import time
from seleniumbase import Driver
import re 


def get_iaai_information(url):
    driver = Driver(
        undetectable=True, block_images=True, page_load_strategy = "eager"
    )
    driver.get(url)
    time.sleep(2)
    driver.execute_script("window.stop();")
    name = driver.find_element("css selector", ".vehicle-header h1").text
    car_name = re.sub(r"\b(19|20)\d{2}\b\s*", "", name)
    car_year = re.search(r"\b(19|20)\d{2}\b\s*", name)
    all_table = driver.find_elements("css selector", ".tile--data")
    vehicle_information = all_table[1]

    odometer_value = ""
    status = ""
    location = ""

    for car_info in vehicle_information.find_elements(
            "css selector", ".data-list__item"
    ):
        label_element = car_info.find_element("css selector", ".data-list__label")
        label_text = label_element.text.strip()
        if label_text.startswith("Start"):
            status = car_info.find_element(
                "css selector", "#startcodeengine_novideo"
            ).text
            if not status:
                status = car_info.find_element(
                    "css selector", "#startcodeengine_image_div"
                ).text
        elif label_text == "Odometer:":
            odometer_value = car_info.find_element(
                "css selector", ".data-list__value"
            ).text
        elif label_text == "Selling Branch:":
            location = car_info.find_element("css selector", ".data-list__value").text
            if location == "Electric Vehicle Auctions":
                location = driver.find_element(
                    "css selector", ".data-list__value-offsite a"
                ).text
    odometer = re.sub(r"\D", "", odometer_value)

    vehicle_description = driver.find_element("#waypoint-trigger").find_element(
        "css selector", ".tile-body"
    )
    for car_description in vehicle_description.find_elements(
            "css selector", ".data-list__item"
    ):
        if (
                car_description.find_element("css selector", ".data-list__label").text
                == "Fuel Type:"
        ):
            fuel_type = car_description.find_element(
                "css selector", ".data-list__value"
            ).text
        elif (
                car_description.find_element("css selector", ".data-list__label").text
                == "Drive Line Type:"
        ):
            drive = car_description.find_element(
                "css selector", ".data-list__value"
            ).text

        elif (
                car_description.find_element("css selector", ".data-list__label").text
                == "Engine:"
        ):
            engine_selector = car_description.find_element(
                "css selector", "#engine_novideo"
            ).text
            if not engine_selector:
                engine_selector = car_description.find_element(
                    "css selector", "#engine_image_div"
                ).text
    engine = re.search(r"(\d+[.,]\d+)", engine_selector)
    message = (
        f"🚗 Назва авто: {car_name}\n"
        f"📅 Рік: {car_year.group(0)}\n"
        f"📏 Пробіг: {odometer}\n"
        f"⛽ Тип палива: {fuel_type}\n"
        f"⚙️ Привід: {drive}\n"
        f"🛠️ Двигун: {engine.group(1) if engine else 'Електро'}{' л' if fuel_type != 'Electric' and engine else ''}\n"
        f"📍 Локація: {location}\n"
    )
    if status:
        message += f"🌟 Стан авто: {status}\n"
    details = {
        "🚗 Назва авто": "Не знайдено",
        "📄 Документи": "Не знайдено",
        "📅 Рік": "Не знайдено",
        "📏 Пробіг": "Не знайдено",
        "⚙️ Привід": "Не знайдено",
        "⛽ Тип палива": "Не знайдено",
        "🛠️ Двигун": "Не знайдено",
        "📍 Локація": "Не знайдено",
        "🌟 Стан авто": "Не знайдено"
    }
    details["🚗 Назва авто"] = car_name
    details["📅 Рік"] = car_year.group(0)
    details["📏 Пробіг"] = odometer
    details["⚙️ Привід"] = drive
    details["🛠️ Двигун"] = engine.group(0)
    details["⛽ Тип палива"] = fuel_type
    details["📍 Локація"] = location
    details["🌟 Стан авто"] = status

    driver.quit()
    return details


async def fetch_car_info(url):
    loop = asyncio.get_running_loop()
    details = await loop.run_in_executor(None, get_iaai_information, url)
    return details