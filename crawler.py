from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import re
import os
import shutil
import streamlit as st

# 🔐 로그인 정보 불러오기
from dotenv import load_dotenv
load_dotenv()

email = os.getenv("UPUP_EMAIL")
password = os.getenv("UPUP_PASSWORD")

def login_and_get_titles(url: str) -> list[str]:
    options = Options()
    # 크롬 & 드라이버 경로 자동 탐색
    chrome_path = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("chromium-browser")
    driver_path = shutil.which("chromedriver")

    st.markdown("### 🧪 경로 확인 테스트")
    st.text(f"Chrome Path: {chrome_path}")
    st.text(f"Chromedriver Path: {driver_path}")
    
    options.binary_location = chrome_path
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')  # 디버깅 시엔 주석 처리
    
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.upup.com/login")
        time.sleep(2)

        # 4. 로그인 정보 입력 및 전송
        email_input = driver.find_element(By.CSS_SELECTOR, "div.email-login input")
        email_input.send_keys(email)

        password_input = driver.find_element(By.CSS_SELECTOR, '#__layout > div > section > main > div > div > div.card-wrap.el-col.el-col-12 > div > div.login-content > div.email-login > div > form > div.el-form-item.from-password.el-form-item--mini > div > div > div > div > input')
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        login_button = driver.find_element(By.CSS_SELECTOR, "#__layout > div > section > main > div > div > div.card-wrap.el-col.el-col-12 > div > div.login-content > div.email-login > div > form > div:nth-child(4) > div > button")
        login_button.click()

        time.sleep(5)  # 로그인 처리 대기

    
        # 랭킹 페이지 이동
        driver.get(url)

        time.sleep(5)

        titles = scroll_until_all_loaded(driver)

    finally:
        driver.quit()

    return titles if titles else ["❌ 앱 타이틀을 찾을 수 없습니다."]


from selenium.webdriver.common.by import By

def scroll_until_all_loaded(driver, max_scrolls=50, pause=2.5):
    from bs4 import BeautifulSoup

    apps = []
    seen_links = set()
    unchanged_rounds = 0
    prev_total_count = 0

    for i in range(max_scrolls):
        print(f"🔽 [{i+1}/{max_scrolls}] 스크롤 중...")
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(pause)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.select("div.dd-hover-row")

        for row in rows:
            name_tag = row.select_one('div.show-text.dd-max-ellipsis a[href^="/app/"]')
            link_tag = row.select_one('div.dd-app a[href^="/app/"]')
            dev_tag = row.select_one('div.develop-info a[href^="/developer/"]')

            cols = row.select('div.el-col')
            try:
                # 전체 순위 등락
                total_rank_box = cols[2]
                total_rank = total_rank_box.select_one(".total-rank div").get_text(strip=True)
                total_rank_change, total_rank_value = get_rank_change_info(total_rank_box)

                # 앱/게임 순위 등락
                app_rank_box = cols[3]
                app_rank = app_rank_box.select_one(".total-rank div").get_text(strip=True)
                app_rank_change, app_rank_value = get_rank_change_info(app_rank_box)

                # 카테고리 순위 + 카테고리명 + 등락
                category_box = cols[4]
                category_rank = category_box.select("div.total-rank div")[0].get_text(strip=True)
                category_name = category_box.select("div.total-rank div")[1].get_text(strip=True)
                category_change, category_value = get_rank_change_info(category_box)
                
                keyword_scope = cols[5].get_text(strip=True)
                rating = cols[6].select_one('span.el-rate__text').get_text(strip=True)
                reviews = cols[7].select_one('span').get_text(strip=True)

                reg_date = ""
                for tag in row.select('div.dd-text-center'):
                    text = tag.get_text(strip=True)
                    if re.match(r"\d{4}-\d{2}-\d{2}", text):
                        reg_date = text
                        break
            except Exception:
                total_rank = category_rank = app_rank = reg_date = keyword_scope = rating = reviews = ""

            if name_tag:
                href = link_tag.get("href", "").strip()
                if href in seen_links:
                    continue
                seen_links.add(href)

                name = name_tag.get_text(strip=True)
                dev = dev_tag.get_text(strip=True) if dev_tag else ""

                apps.append({
                    "name": name,
                    "href": href,
                    "developer": dev,
                    "total_rank": total_rank,
                    "total_rank_change":total_rank_change,
                    "total_rank_value": total_rank_value,
                    "app_rank" : app_rank,
                    "app_rank_change": app_rank_change,
                    "app_rank_value": app_rank_value,
                    "category_name": category_name,
                    "category_rank": category_rank,
                    "category_change": category_change,
                    "category_value": category_value,
                    "keyword_scope": keyword_scope,
                    "rating": rating,
                    "reviews": reviews,
                    "reg_date": reg_date
                })

        total_count = len(apps)
        print(f"📦 현재까지 앱 수: {total_count}")

        if total_count == prev_total_count:
            unchanged_rounds += 1
            if unchanged_rounds >= 3:
                print("✅ 3회 연속 변화 없음 → 스크롤 중단")
                break
        else:
            unchanged_rounds = 0

        prev_total_count = total_count

    return apps


def get_rank_change_info(rank_div):
    up = rank_div.select_one(".icon-up")
    down = rank_div.select_one(".icon-down")
    
    if up:
        direction = "up"
        value = up.get_text(strip=True)
    elif down:
        direction = "down"
        value = down.get_text(strip=True)
    else:
        direction = "same"
        value = ""
    return direction, value