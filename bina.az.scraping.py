# ilk öncə lazımi kitabxanalar çağırılır

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

data = []   # məlumatların yaddaşda saxlanılması üçün boş bir array yaradılır


options = webdriver.EdgeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Edge(options=options)
driver.get(
    # məlumatların emal olunacağı başlanğıc səhifənin linki istəyə görə yerləşdirilir
    "https://bina.az/baki/alqi-satqi/menziller/yeni-tikili?has_bill_of_sale=true&has_repair=true&location_ids%5B%5D=5&location_ids%5B%5D=8&location_ids%5B%5D=279&location_ids%5B%5D=266&location_ids%5B%5D=6&location_ids%5B%5D=63&location_ids%5B%5D=61&location_ids%5B%5D=37&location_ids%5B%5D=315&location_ids%5B%5D=54&location_ids%5B%5D=33&location_ids%5B%5D=2&location_ids%5B%5D=51&location_ids%5B%5D=34&location_ids%5B%5D=7&location_ids%5B%5D=4&location_ids%5B%5D=52&location_ids%5B%5D=59&location_ids%5B%5D=53&location_ids%5B%5D=1&location_ids%5B%5D=60&location_ids%5B%5D=3&location_ids%5B%5D=36&location_ids%5B%5D=38&location_ids%5B%5D=35")
time.sleep(2) # səhifənin tamamlanması üçün 2 saniyəlik gözləmə

main_window = driver.current_window_handle  # susmaya görə əsas pəncərənin seçilməsi

all_links = set()  # hər individual elan linklərinin təkrarlanmadan qeyd olunması


# səhifə dinamik olduğu üçün istədiyimiz elan sayına qədər səhifənin aşağıya doğru çəkilməsi
item_limit = 3000  # Maksimum elan sayı (istəyə görə dəyişdirilir)

# Scroll prosesi
last_height = driver.execute_script("return document.body.scrollHeight")  # ilkin səhifə genişliyinin qeyd olunması

while True:
    # Mövcud elan sayının hesablanma prosesi
    cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="item-card"]')

    for card in cards:  # elan ünvanlarının əlavə edilməsi. cards-dakı elementlər artdıqca proses ləngiyir.
        try:
            href = card.find_element(By.TAG_NAME, 'a').get_attribute("href")
            if href and href.startswith("https://bina.az/items/"):
                all_links.add(href)
        except:
            pass

    print(" Toplanan elan sayı:", len(all_links))  # elan sayını hər scroll sonrası əks etdirir

    # aşağı sürüşdür
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)  # səhifənin 1 saniyə gözləmə ilə aşağıya sürüşdürülməsi

    # Yeni səhifə uzunluğunu yoxlayırıq
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height or len(all_links) >= item_limit:
        print("Scroll dayandırıldı")
        break

    last_height = new_height  # davam etdiyimiz təqdirdə yeni uzunluq son uzunluğu əvəz edir

time.sleep(5)

# 2. Məlumatları toplayırıq
for index, card in enumerate(cards[:item_limit]):
    try:
        link_element = card.find_element(By.TAG_NAME, 'a')  # ardıcıl olaraq indekslənmiş elanların ünvanları əldə olunur.
        href = link_element.get_attribute("href")

        # Yeni pəncərə aç
        driver.execute_script("window.open(arguments[0]);", href)  # elan ünvana görə yeni pəncərədə açılır
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[-1])  # açılan pəncərə əməliyyat aparılması üçün seçilir
        try:
            # lazımi məlumatlar müxtəlif üsullarla əldə olunur. susmaya görə məlumatlar qeyd olunmadığı
            # təqdirdə Tapılmadı olaraq işarələnir

            info_blocks = driver.find_elements(By.CLASS_NAME, "product-properties__i")
            prices = driver.find_elements(By.CLASS_NAME, "product-price")
            bedroom = floor = area = location = certificate = category = price = "Tapılmadı"
            head = driver.find_elements(By.CLASS_NAME, "product-heading-container")


            # aşağıdakı sətirlərdə məlumatlar uyğun dəyişənlərə köçürülür
            for h in head:
                try:
                    valh = h.find_element(By.CLASS_NAME, 'product-title').text.strip()
                    location = valh
                except:
                    continue
            for p in prices:
                try:
                    valp = p.find_element(By.CLASS_NAME, "price-val").text.strip()
                    price = valp
                except:
                    continue

            for block in info_blocks:
                try:
                    label = block.find_element(By.CLASS_NAME, "product-properties__i-name").text.strip().lower()
                    value = block.find_element(By.CLASS_NAME, "product-properties__i-value").text.strip()

                    if "sahə" in label:
                        area = value
                    elif "otaq sayı" in label:
                        bedroom = value
                    elif "mərtəbə" in label:
                        floor = value
                    elif "çıxarış" in label:
                        certificate = value
                    elif "kateqoriya" in label:
                        category = value

                except:
                    continue

            #  tapılmış məlumatlar array-da saxlanılır

            data.append({
                "Elan No": index + 1,
                "Otaq sayı": bedroom,
                "Mərtəbə": floor,
                "Qiymət": price,
                "Sahə": area,
                "Yerləşdiyi ərazi": location,
                "Çıxarış": certificate,
            })

            # proses gedərkən izləmək üçün məlumatların yoxlanılması
            print(f"{index + 1}. OK: {bedroom} | {floor} | {price} | {area} | {location} | {certificate}")

        except Exception as e:
            print(f"{index + 1}. məlumat əldə olunmadı: {e}")

        # Pəncərəni bağlayırıq
        driver.close()
        driver.switch_to.window(main_window)  # davam etmək üçün susmaya görə əsas pəncərəni seçirik

    except Exception as e:
        print(f"Xəta baş verdi: {e}")
        continue

driver.quit()  # webdriver-i sonlandırırıq


#  data array-ini excel faylı kimi yaddaşda saxlayırıq.
import pandas as pd

df = pd.DataFrame(data)
df.to_excel(r"C:\Users\cavid\Desktop\output.xlsx", index=False)