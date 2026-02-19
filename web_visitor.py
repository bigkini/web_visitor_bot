import asyncio
import random
import os
import json
from datetime import datetime
from playwright.async_api import async_playwright
from playwright_stealth import stealth

# 1. kini 님의 전체 User-Agent 리스트 (패턴 분석 회피용)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Edg/121.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/121.0.6167.138 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-S918N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-A536N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; SM-S926N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-G998N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; LM-V500N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Whale/3.24.223.18 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Whale/3.24.223.18 Safari/537.36',
]

def load_urls():
    """URL 목록 로드 (중복 제거 포함)"""
    urls = set() # 처음부터 set을 사용하여 중복 방지
    
    if os.path.exists('urls.txt'):
        with open('urls.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.add(line)
    
    env_urls = os.environ.get('TARGET_URLS')
    if env_urls:
        try:
            for u in json.loads(env_urls): urls.add(u)
        except:
            urls.add(env_urls)
            
    return list(urls)

async def human_behavior(page):
    """실제 사람처럼 행동 시뮬레이션"""
    # 1. 랜덤 스크롤
    for _ in range(random.randint(3, 6)):
        scroll_y = random.randint(300, 700)
        await page.mouse.wheel(0, scroll_y)
        await asyncio.sleep(random.uniform(1.0, 2.5))
    
    # 2. 마우스 미세 이동
    await page.mouse.move(random.randint(100, 800), random.randint(100, 800))
    await asyncio.sleep(random.uniform(3, 8)) # 실제 기사를 읽는 듯한 체류 시간

async def main():
    urls = load_urls()
    if not urls:
        print("❌ 방문할 URL이 없습니다.")
        return

    # 정확히 5회씩 방문하도록 스케줄 생성 (버그 수정됨)
    visit_schedule = []
    for url in urls:
        for _ in range(5):
            visit_schedule.append(url)
    random.shuffle(visit_schedule)

    total = len(visit_schedule)
    print(f"📋 고유 URL: {len(urls)}개 / 총 방문 예정: {total}회")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 전체 실행 동안 하나의 세션을 유지하되 UA는 랜덤하게 교체 가능 (필요시)
        ua = random.choice(USER_AGENTS)
        context = await browser.new_context(
            user_agent=ua,
            viewport={'width': 1920, 'height': 1080},
            locale="ko-KR",
            timezone_id="Asia/Seoul"
        )

        counts = {url: 0 for url in urls}

        for i, url in enumerate(visit_schedule, 1):
            counts[url] += 1
            now = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{now}] 🌐 [{i}/{total}] {url} ({counts[url]}/5회차)")
            
            page = await context.new_page()
            await stealth_async(page) # 스텔스 모드 적용
            
            try:
                # 네이버 유입 경로 위장
                await page.goto(url, wait_until="networkidle", referer="https://www.naver.com/")
                await human_behavior(page)
                print(f"✅ 방문 성공: {await page.title()[:20]}...")
            except Exception as e:
                print(f"❌ 오류: {str(e)[:50]}")
            finally:
                await page.close()

            # 다음 방문 전 랜덤 대기
            if i < total:
                wait = random.randint(45, 150)
                # 10% 확률로 대폭 휴식
                if random.random() < 0.1: 
                    wait += random.randint(300, 600)
                    print("💤 장기 휴식 모드 발동")
                print(f"⏰ {wait}초 대기 중...")
                await asyncio.sleep(wait)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
