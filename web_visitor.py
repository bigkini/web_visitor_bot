import requests
import random
import time
import json
from datetime import datetime
import os

# 한국 사용자 환경에 맞춘 User-Agent 목록
USER_AGENTS = [
    # Chrome (Windows) - 한국에서 가장 많이 사용
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    
    # Edge (Windows) - 한국 기업에서 많이 사용
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    
    # Safari (Mac) - 맥북 사용자
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    
    # 모바일 (iPhone) - 한국에서 아이폰 사용률 높음
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/121.0.6167.138 Mobile/15E148 Safari/604.1',
    
    # 모바일 (Samsung Galaxy) - 한국 안드로이드 대표
    'Mozilla/5.0 (Linux; Android 14; SM-S918N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-A536N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; SM-S926N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-G998N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
    
    # LG 스마트폰 (한국 브랜드)
    'Mozilla/5.0 (Linux; Android 12; LM-V500N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
    
    # Firefox (일부 사용자)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
    
    # 네이버 웨일 브라우저 (한국 브라우저)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Whale/3.24.223.18 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Whale/3.24.223.18 Safari/537.36',
]

# 한국 사용자 환경에 맞춘 Accept-Language 목록
KOREAN_ACCEPT_LANGUAGES = [
    'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',  # 가장 일반적
    'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
    'ko,en-US;q=0.9,en;q=0.8',
    'ko-KR,en-US;q=0.9,ko;q=0.8,en;q=0.7',
    'ko-KR;q=1.0,ko;q=0.9,en;q=0.8',
]

def load_urls():
    """URL 목록 로드"""
    urls = []
    
    # 1. urls.txt 파일에서 로드
    if os.path.exists('urls.txt'):
        with open('urls.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
    
    # 2. 환경변수에서 로드 (JSON 형식)
    env_urls = os.environ.get('TARGET_URLS')
    if env_urls:
        try:
            urls.extend(json.loads(env_urls))
        except json.JSONDecodeError:
            # 단일 URL인 경우
            urls.append(env_urls)
    
    # 3. 기본 URL (환경변수)
    single_url = os.environ.get('TARGET_URL')
    if single_url and single_url not in urls:
        urls.append(single_url)
    
    # 4. 기본값
    if not urls:
        urls = ['https://example.com']
    
    return urls

def get_random_delay():
    """더 자연스러운 랜덤 대기시간 생성"""
    # 다양한 대기 패턴을 랜덤하게 선택
    delay_patterns = [
        # 짧은 대기 (30초~3분) - 40%
        lambda: random.randint(30, 180),
        lambda: random.randint(30, 180),
        lambda: random.randint(30, 180),
        lambda: random.randint(30, 180),
        
        # 중간 대기 (3분~8분) - 40% 
        lambda: random.randint(180, 480),
        lambda: random.randint(180, 480),
        lambda: random.randint(180, 480),
        lambda: random.randint(180, 480),
        
        # 긴 대기 (8분~15분) - 20%
        lambda: random.randint(480, 900),
        lambda: random.randint(480, 900),
    ]
    
    # 랜덤하게 패턴 선택해서 대기시간 생성
    selected_pattern = random.choice(delay_patterns)
    base_delay = selected_pattern()
    
    # 10% 확률로 추가 휴식 시간 (실제 사람처럼)
    if random.random() < 0.1:
        extra_rest = random.randint(300, 1200)  # 5~20분 추가
        print("💤 추가 휴식 시간이 적용됩니다")
        return base_delay + extra_rest
    
    return base_delay

def visit_page(url, visit_number, total_visits):
    """페이지 방문 함수"""
    try:
        # 랜덤한 User-Agent 선택 (한국 환경에 맞춤)
        user_agent = random.choice(USER_AGENTS)
        
        # 한국 시간대 고려한 더 자연스러운 헤더
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': random.choice(KOREAN_ACCEPT_LANGUAGES),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'same-site']),
            'Sec-Fetch-User': '?1',
            'Cache-Control': random.choice(['no-cache', 'max-age=0', '']),
            'sec-ch-ua': get_sec_ch_ua(user_agent),
            'sec-ch-ua-mobile': get_mobile_hint(user_agent),
            'sec-ch-ua-platform': get_platform_hint(user_agent),
        }
        
        # 모바일인 경우 viewport 헤더 추가
        if 'Mobile' in user_agent:
            headers['Viewport-Width'] = str(random.choice([360, 375, 390, 412, 414]))
        
        # 요청 보내기
        response = requests.get(url, headers=headers, timeout=30)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        device_type = get_device_type(user_agent)
        
        if response.status_code == 200:
            print(f"[{current_time}] ✅ 방문 {visit_number}/{total_visits} 성공")
            print(f"  🌐 URL: {url}")
            print(f"  📱 기기: {device_type}")
            print(f"  🔧 브라우저: {get_browser_name(user_agent)}")
        else:
            print(f"[{current_time}] ❌ 방문 {visit_number}/{total_visits} 실패")
            print(f"  🌐 URL: {url}")
            print(f"  📊 상태코드: {response.status_code}")
            
        return True
        
    except Exception as e:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] 💥 방문 {visit_number}/{total_visits} 오류")
        print(f"  🌐 URL: {url}")
        print(f"  ⚠️  오류: {str(e)}")
        return False

def get_sec_ch_ua(user_agent):
    """User-Agent에 맞는 sec-ch-ua 헤더 생성"""
    if 'Whale' in user_agent:
        return '"Whale";v="3", "Not-A.Brand";v="8", "Chromium";v="121"'
    elif 'Edg' in user_agent:
        return '"Microsoft Edge";v="121", "Not-A.Brand";v="99", "Chromium";v="121"'
    elif 'Chrome' in user_agent and 'Safari' in user_agent:
        return '"Google Chrome";v="121", "Not-A.Brand";v="99", "Chromium";v="121"'
    elif 'Firefox' in user_agent:
        return '"Firefox";v="122", "Not-A.Brand";v="99"'
    elif 'Safari' in user_agent and 'Chrome' not in user_agent:
        return '"Safari";v="17", "Not-A.Brand";v="99"'
    else:
        return '"Chromium";v="121", "Not-A.Brand";v="99"'

def get_mobile_hint(user_agent):
    """모바일 힌트 반환"""
    return "?1" if 'Mobile' in user_agent or 'iPhone' in user_agent else "?0"

def get_platform_hint(user_agent):
    """플랫폼 힌트 반환"""
    if 'Windows NT 10.0' in user_agent:
        return '"Windows"'
    elif 'Windows NT 11.0' in user_agent:
        return '"Windows"'
    elif 'Macintosh' in user_agent:
        return '"macOS"'
    elif 'iPhone' in user_agent:
        return '"iOS"'
    elif 'Android' in user_agent:
        return '"Android"'
    else:
        return '"Windows"'

def get_device_type(user_agent):
    """기기 타입 반환 (로그용)"""
    if 'iPhone' in user_agent:
        return "iPhone"
    elif 'SM-S918N' in user_agent:
        return "Galaxy S23 Ultra"
    elif 'SM-S926N' in user_agent:
        return "Galaxy S24+"
    elif 'SM-A536N' in user_agent:
        return "Galaxy A53"
    elif 'SM-G998N' in user_agent:
        return "Galaxy S21 Ultra"
    elif 'LM-V500N' in user_agent:
        return "LG V50"
    elif 'Android' in user_agent:
        return "Android"
    elif 'Macintosh' in user_agent:
        return "Mac"
    elif 'Windows NT 11' in user_agent:
        return "Windows 11"
    elif 'Windows NT 10' in user_agent:
        return "Windows 10"
    else:
        return "PC"

def get_browser_name(user_agent):
    """브라우저 이름 반환 (로그용)"""
    if 'Whale' in user_agent:
        return "네이버 웨일"
    elif 'Edg' in user_agent:
        return "Microsoft Edge"
    elif 'Chrome' in user_agent and 'CriOS' in user_agent:
        return "Chrome (iOS)"
    elif 'Chrome' in user_agent:
        return "Chrome"
    elif 'Firefox' in user_agent:
        return "Firefox"
    elif 'Safari' in user_agent and 'Chrome' not in user_agent:
        return "Safari"
    else:
        return "Unknown"

def create_visit_schedule(urls):
    """방문 스케줄 생성 (완전 랜덤)"""
    # 각 URL을 5번씩 복제해서 전체 방문 목록 만들기
    visit_list = []
    for url in urls:
        for _ in range(5):
            visit_list.append(url)
    
    # 완전히 랜덤하게 섞기
    random.shuffle(visit_list)
    
    return visit_list

def main():
    # URL 목록 로드
    urls = load_urls()
    
    if not urls:
        print("❌ 방문할 URL이 없습니다!")
        return
    
    # 랜덤 방문 스케줄 생성
    visit_schedule = create_visit_schedule(urls)
    total_visits = len(visit_schedule)
    
    print(f"📋 로드된 URL 개수: {len(urls)}")
    print(f"🎯 총 방문 횟수: {total_visits} (각 URL당 5회)")
    print(f"🎲 랜덤 방문 순서로 실행합니다")
    print("=" * 60)
    
    # URL별 방문 카운트 추적
    visit_counts = {url: 0 for url in urls}
    
    # 랜덤 순서로 방문 실행
    for i, url in enumerate(visit_schedule, 1):
        visit_counts[url] += 1
        current_visit_for_url = visit_counts[url]
        
        print(f"\n🌐 [{i}/{total_visits}] {url}")
        print(f"   (이 URL의 {current_visit_for_url}/5번째 방문)")
        print("-" * 50)
        
        visit_page(url, i, total_visits)
        
        # 마지막 방문이 아니면 랜덤 대기
        if i < total_visits:
            wait_time = get_random_delay()
            minutes, seconds = divmod(wait_time, 60)
            print(f"⏰ 다음 방문까지 {minutes}분 {seconds}초 대기...")
            time.sleep(wait_time)
    
    print("\n" + "=" * 60)
    print("🎉 모든 방문 완료!")
    print(f"총 {total_visits}번 방문했습니다.")
    
    # 방문 결과 요약
    print("\n📊 방문 결과 요약:")
    for url, count in visit_counts.items():
        print(f"  • {url}: {count}/5회")

if __name__ == "__main__":
    main()
