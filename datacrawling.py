from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json
import time

# Selenium WebDriver 설정
options = webdriver.ChromeOptions()
options.add_argument("--force-device-scale-factor=0.05")  # 화면 비율 조정
driver = webdriver.Chrome(options=options)

# 메인 페이지 URL
base_url = "https://card-search.naver.com/list"
driver.get(base_url)

# 데이터 저장 리스트
card_links = []  # 카드 링크 저장
card_info_data = []  # CardInfo.json 저장용
card_benefits_data = []  # card_data_benefits.json 저장용
card_image_data = []  # CardImage.csv 저장용


def collect_card_links():
    """카드 링크를 수집하는 함수"""
    try:
        # 카드 목록 로드 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list li.item"))
        )

        while True:
            # 카드 링크 수집
            cards = driver.find_elements(By.CSS_SELECTOR, "ul.list li.item a.anchor")
            for card in cards:
                link = card.get_attribute("href")
                if link and link not in card_links:  # 중복 및 None 방지
                    card_links.append(link)

            # "더보기" 버튼 클릭
            try:
                more_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.more"))
                )
                ActionChains(driver).move_to_element(more_button).click().perform()
                time.sleep(1)  # 로드 대기
            except Exception as e:
                print("No more button found or error clicking:", e)
                break

        print(f"Total card links collected: {len(card_links)}")

    except Exception as e:
        print(f"Error collecting card links: {e}")


def extract_benefits():
    """혜택 상세 내역 추출"""
    benefits = []
    try:
        # div[3]과 div[4] 탐색
        for div_index in [3, 4]:
            try:
                div_route = driver.find_element(By.XPATH, f"/html/body/div/div/div[{div_index}]/div")
                details_elements = div_route.find_elements(By.TAG_NAME, "details")

                for j in range(1, len(details_elements) + 1):
                    try:
                        # details 클릭
                        button_click = driver.find_element(By.XPATH, f"/html/body/div/div/div[{div_index}]/div/details[{j}]")
                        button_click.click()
                        time.sleep(1)

                        # 텍스트 수집
                        button_names = [el.text for el in driver.find_elements(By.XPATH, f"/html/body/div/div/div[{div_index}]/div/details[{j}]/summary/h5/b")]
                        details_titles = [el.text for el in driver.find_elements(By.XPATH, f"/html/body/div/div/div[{div_index}]/div/details[{j}]/div/dl/dt")]
                        details_list = [el.text for el in driver.find_elements(By.XPATH, f"/html/body/div/div/div[{div_index}]/div/details[{j}]/div/dl/dd")]

                        # 하나의 혜택 카테고리 저장
                        benefits.append({
                            "Category": button_names,
                            "Title": details_titles,
                            "More_Details": details_list
                        })

                    except Exception as e:
                        print(f"Error clicking details in div {div_index}, index {j}: {e}")

            except Exception as e:
                print(f"Error finding div {div_index}: {e}")

    except Exception as e:
        print(f"Error extracting benefits: {e}")

    return benefits


def process_card(card_id, card_link):
    """카드 상세 정보를 수집하는 함수"""
    driver.get(card_link)
    time.sleep(1)  # 페이지 로드 대기

    try:
        # 공통 정보 수집
        card_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.cardname b.txt"))
        ).text

        annual_fee = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "dd.desc.as_annualFee span.txt"))
        ).text

        base_record = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "dd.desc.as_baseRecord span.txt"))
        ).text

        try:
            card_apply_url = driver.find_element(By.CSS_SELECTOR, "a.apply").get_attribute("href")
        except:
            card_apply_url = "N/A"

        # CardInfo.json 데이터 저장
        card_info_data.append({
            "cardId": card_id,
            "cardName": card_name,
            "annualFee": annual_fee,
            "prevSales": base_record,
            "cardApplyUrl": card_apply_url
        })

        # card_data_benefits.json 데이터 저장
        benefits = extract_benefits()
        card_benefits_data.append({
            "cardId": card_id,
            "Card Name": card_name,
            "Annual_fee": annual_fee,
            "Base Record": base_record,
            "Benefits": benefits
        })

    except Exception as e:
        print(f"Error processing card: {card_link}, Error: {e}")


def collect_card_images():
    """카드 ID와 이미지 URL 수집"""
    card_items = driver.find_elements(By.CSS_SELECTOR, "ul.list li.item")
    for idx, card in enumerate(card_items, start=1):  # cardId는 1부터 시작
        try:
            image_url = card.find_element(By.CSS_SELECTOR, "div.preview img.img").get_attribute("src")
            card_image_data.append({
                "cardId": idx,
                "ImageURL": image_url
            })
        except Exception as e:
            print(f"Error processing card image: {e}")


try:
    # Step 1: 카드 링크 수집
    collect_card_links()

    # Step 2: 카드 이미지 수집 (먼저 실행)
    collect_card_images()

    # Step 3: 카드 세부 정보 수집
    for idx, link in enumerate(card_links, start=1):
        process_card(idx, link)

finally:
    driver.quit()

# 파일 저장
# CardInfo.json 저장
with open("./data/CardInfo.json", "w", encoding="utf-8") as json_file:
    json.dump(card_info_data, json_file, ensure_ascii=False, indent=4)
print("Data saved to CardInfo.json")

# card_data_benefits.json 저장
with open("./data/card_data_benefits.json", "w", encoding="utf-8") as json_file:
    json.dump(card_benefits_data, json_file, ensure_ascii=False, indent=4)
print("Data saved to card_data_benefits.json")

# CardImage.csv 저장
df = pd.DataFrame(card_image_data)
df.to_csv("./data/CardImage.csv", index=False)
print("Data saved to CardImage.csv")
