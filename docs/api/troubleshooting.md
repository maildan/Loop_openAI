# API 문제 해결 가이드

Loop AI API 사용 중 발생할 수 있는 문제들과 해결 방법을 제공합니다.

## 📋 목차
- [연결 문제](#연결-문제)
- [Fantasy Name Generator 문제](#fantasy-name-generator-문제)
- [Story Generator 문제](#story-generator-문제)
- [성능 최적화](#성능-최적화)
- [에러 코드 가이드](#에러-코드-가이드)
- [디버깅 도구](#디버깅-도구)

## 🔌 연결 문제

### 1. 서버에 연결할 수 없습니다

**증상:**
```
ConnectionError: Failed to establish a new connection
```

**원인 및 해결방법:**

1. **서버가 실행 중인지 확인**
   ```bash
   # 서버 상태 확인
   curl http://localhost:8000/api/health
   
   # 서버 실행 (백그라운드)
   python src/inference/server.py &
   ```

2. **포트 충돌 확인**
   ```bash
   # 8000번 포트 사용 프로세스 확인
   lsof -i :8000
   
   # 프로세스 종료 후 재시작
   kill -9 <PID>
   python src/inference/server.py
   ```

3. **방화벽 설정 확인**
   ```bash
   # macOS 방화벽 확인
   sudo pfctl -sr | grep 8000
   
   # Windows 방화벽 확인
   netsh advfirewall firewall show rule name="Port 8000"
   ```

### 2. CORS 에러

**증상:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**해결방법:**

1. **서버 설정 확인** (`src/inference/server.py`)
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인 지정
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **프록시 설정** (개발 환경)
   ```javascript
   // package.json (React)
   "proxy": "http://localhost:8000"
   
   // 또는 axios 설정
   axios.defaults.baseURL = 'http://localhost:8000';
   ```

## 🎭 Fantasy Name Generator 문제

### 1. 같은 이름이 반복 생성됨

**증상:**
동일한 파라미터로 요청 시 계속 같은 이름이 나옴

**해결방법:**

1. **스타일 변경**
   ```bash
   curl -X POST "http://localhost:8000/api/names/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "style": "mixed",  # "anime" 대신 "mixed" 사용
       "count": 5
     }'
   ```

2. **파라미터 조합**
   ```python
   # 다양한 조합으로 생성
   params_list = [
       {"gender": "female", "style": "anime", "character_class": "마법사"},
       {"gender": "female", "style": "western", "element": "fire"},
       {"gender": "female", "style": "composed"},
   ]
   
   for params in params_list:
       response = requests.post(url, json=params)
   ```

### 2. 원하지 않는 성별의 이름 생성

**증상:**
`gender: "male"`로 설정했는데 여성 이름이 나옴

**해결방법:**

1. **명시적 성별 지정**
   ```json
   {
     "gender": "male",
     "style": "western",  // 서양 스타일은 성별 구분이 더 명확
     "character_class": "기사"
   }
   ```

2. **후처리 필터링**
   ```python
   def filter_by_gender(names, target_gender):
       # 간단한 휴리스틱 필터링
       male_endings = ['스', '트', '드', '르', '온']
       female_endings = ['아', '나', '리', '미', '사']
       
       filtered = []
       for name_obj in names:
           name = name_obj['name']
           if target_gender == 'male' and name[-1] in male_endings:
               filtered.append(name_obj)
           elif target_gender == 'female' and name[-1] in female_endings:
               filtered.append(name_obj)
       
       return filtered
   ```

### 3. 원소 속성이 반영되지 않음

**증상:**
`element: "fire"`로 설정했는데 불과 관련 없는 이름이 나옴

**해결방법:**

1. **클래스와 원소 조합**
   ```bash
   curl -X POST "http://localhost:8000/api/names/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "character_class": "마법사",
       "element": "fire",
       "count": 5
     }'
   ```

2. **원소 목록 확인**
   ```bash
   # 사용 가능한 원소 확인
   curl http://localhost:8000/api/names/elements
   ```

## 📖 Story Generator 문제

### 1. 너무 짧은 스토리 생성

**증상:**
1-2 문장만 생성되고 끝남

**해결방법:**

1. **토큰 수 증가**
   ```python
   response = requests.post(url, json={
       "prompt": "상세하고 긴 이야기를 써줘",
       "max_new_tokens": 800,  # 기본값 512보다 증가
       "temperature": 0.7
   })
   ```

2. **프롬프트 개선**
   ```python
   # 나쁜 예
   prompt = "이야기 써줘"
   
   # 좋은 예  
   prompt = """
   마법학교에 입학한 주인공이 첫 시험에서 예상치 못한 능력을 발견하고,
   이로 인해 벌어지는 모험을 자세히 써줘. 
   등장인물들의 심리 묘사와 마법 시스템에 대한 설명도 포함해줘.
   """
   ```

### 2. 반복적인 내용 생성

**증상:**
같은 문장이나 단어가 계속 반복됨

**해결방법:**

1. **온도 조정**
   ```python
   # 반복이 심할 때
   params = {
       "temperature": 0.8,  # 0.5에서 0.8로 증가
       "max_new_tokens": 500
   }
   ```

2. **프롬프트 다양화**
   ```python
   # 매번 다른 시작점 제공
   import random
   
   starters = [
       "갑자기",
       "그때였다",
       "하지만",
       "한편",
       "놀랍게도"
   ]
   
   prompt = f"{random.choice(starters)}, {original_prompt}"
   ```

### 3. 잘못된 장르의 내용 생성

**증상:**
`genre: "romance"`인데 액션 장면이 나옴

**해결방법:**

1. **장르 키워드 포함**
   ```python
   genre_keywords = {
       "romance": "사랑, 감정, 마음, 설렘, 연인",
       "fantasy": "마법, 모험, 용, 마법사, 왕국",
       "sf": "미래, 로봇, 우주, 기술, 과학",
       "mystery": "수수께끼, 단서, 추리, 범인, 비밀"
   }
   
   prompt = f"{original_prompt}. {genre_keywords[genre]} 요소를 포함해서 써줘."
   ```

2. **장르별 최적 설정 사용**
   ```python
   genre_settings = {
       "fantasy": {"temperature": 0.8, "max_new_tokens": 600},
       "romance": {"temperature": 0.7, "max_new_tokens": 500},
       "sf": {"temperature": 0.6, "max_new_tokens": 700},
       "mystery": {"temperature": 0.5, "max_new_tokens": 600}
   }
   
   settings = genre_settings.get(genre, {"temperature": 0.7, "max_new_tokens": 500})
   ```

## 🚀 성능 최적화

### 1. 느린 응답 시간

**문제 진단:**

1. **서버 리소스 확인**
   ```bash
   # CPU 사용률 확인
   top -p $(pgrep -f "python.*server.py")
   
   # 메모리 사용량 확인
   ps aux | grep "python.*server.py"
   
   # GPU 사용량 확인 (CUDA 환경)
   nvidia-smi
   ```

2. **모델 로딩 상태 확인**
   ```python
   # 헬스체크로 모델 상태 확인
   import requests
   response = requests.get("http://localhost:8000/api/health")
   print(response.json())
   ```

**최적화 방법:**

1. **배치 처리**
   ```python
   # 나쁜 예: 순차 처리
   for i in range(10):
       response = requests.post(url, json={"count": 1})
   
   # 좋은 예: 배치 처리
   response = requests.post(url, json={"count": 10})
   ```

2. **모델 캐싱**
   ```python
   # 서버에서 모델을 한 번만 로드하도록 확인
   # src/inference/server.py 확인
   ```

### 2. 메모리 부족

**증상:**
```
CUDA out of memory
RuntimeError: out of memory
```

**해결방법:**

1. **토큰 수 줄이기**
   ```python
   # 메모리 부족 시
   params = {
       "max_new_tokens": 300,  # 기본값을 낮춤
       "temperature": 0.7
   }
   ```

2. **배치 크기 조정**
   ```python
   # 한 번에 많은 이름을 생성하지 말고 나누어서 처리
   def generate_large_batch(total_count):
       batch_size = 5
       all_names = []
       
       for i in range(0, total_count, batch_size):
           current_batch = min(batch_size, total_count - i)
           response = requests.post(url, json={"count": current_batch})
           all_names.extend(response.json()['names'])
           
           time.sleep(0.5)  # 메모리 정리 시간
       
       return all_names
   ```

## 📊 에러 코드 가이드

### HTTP 400 - Bad Request

**일반적인 원인:**

1. **필수 파라미터 누락**
   ```python
   # 잘못된 요청
   response = requests.post(url, json={})  # prompt 누락
   
   # 올바른 요청
   response = requests.post(url, json={"prompt": "이야기를 써줘"})
   ```

2. **잘못된 파라미터 값**
   ```python
   # 잘못된 값
   {
       "temperature": 2.0,  # 최대값 1.0 초과
       "max_new_tokens": 2000,  # 최대값 1000 초과
       "genre": "invalid_genre"  # 지원하지 않는 장르
   }
   
   # 올바른 값
   {
       "temperature": 0.8,
       "max_new_tokens": 500,
       "genre": "fantasy"
   }
   ```

### HTTP 422 - Unprocessable Entity

**해결방법:**

1. **파라미터 타입 확인**
   ```python
   # 잘못된 타입
   {
       "count": "5",  # 문자열 대신 숫자 필요
       "temperature": "0.7"
   }
   
   # 올바른 타입
   {
       "count": 5,
       "temperature": 0.7
   }
   ```

2. **범위 확인**
   ```python
   # 범위 초과
   {
       "count": 25,  # 최대 20
       "temperature": -0.1  # 최소 0.1
   }
   ```

### HTTP 500 - Internal Server Error

**진단 및 해결:**

1. **서버 로그 확인**
   ```bash
   tail -f server.log
   ```

2. **모델 상태 확인**
   ```bash
   # 서버 재시작
   pkill -f "python.*server.py"
   python src/inference/server.py > server.log 2>&1 &
   ```

## 🔧 디버깅 도구

### 1. API 요청 테스트 도구

#### 간단한 테스트 스크립트
```python
#!/usr/bin/env python3
"""
Loop AI API 테스트 스크립트
"""

import requests
import json
import time

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def test_health(self):
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            print(f"✅ Health Check: {response.status_code}")
            print(f"Response: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ Health Check Failed: {e}")
            return False
    
    def test_name_generation(self):
        """이름 생성 테스트"""
        test_cases = [
            {"gender": "female", "style": "anime", "count": 3},
            {"gender": "male", "character_class": "기사", "count": 2},
            {"element": "fire", "character_class": "마법사", "count": 2}
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\n🎭 Name Test {i}: {params}")
            try:
                response = requests.post(
                    f"{self.base_url}/api/names/generate",
                    json=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Generated {len(data['names'])} names")
                    for name in data['names']:
                        print(f"  - {name['name']} ({name.get('type', 'N/A')})")
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"❌ Test {i} Failed: {e}")
    
    def test_story_generation(self):
        """스토리 생성 테스트"""
        test_cases = [
            {
                "prompt": "짧은 판타지 이야기",
                "genre": "fantasy",
                "max_new_tokens": 200
            },
            {
                "prompt": "로맨스 한 장면",
                "genre": "romance",
                "temperature": 0.8,
                "max_new_tokens": 150
            }
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\n📖 Story Test {i}: {params['prompt']}")
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=params,
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Generated in {end_time - start_time:.2f}s")
                    print(f"Tokens: {data['metadata']['actual_tokens']}")
                    print(f"Story: {data['generated_text'][:100]}...")
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"❌ Test {i} Failed: {e}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 Starting Loop AI API Tests...")
        
        if not self.test_health():
            print("❌ Server is not healthy. Stopping tests.")
            return
        
        self.test_name_generation()
        self.test_story_generation()
        
        print("\n✅ All tests completed!")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
```

### 2. 성능 모니터링

#### 서버 모니터링 스크립트
```bash
#!/bin/bash
# monitor_api.sh

echo "🔍 Loop AI API 모니터링 시작..."

# 서버 프로세스 확인
echo "📊 서버 프로세스:"
ps aux | grep "python.*server.py" | grep -v grep

# 포트 확인
echo -e "\n🔌 포트 상태:"
netstat -tlnp | grep :8000

# 메모리 사용량
echo -e "\n💾 메모리 사용량:"
free -h

# API 응답 시간 테스트
echo -e "\n⏱️ API 응답 시간:"
for i in {1..5}; do
    start_time=$(date +%s.%N)
    curl -s -o /dev/null http://localhost:8000/api/health
    end_time=$(date +%s.%N)
    response_time=$(echo "$end_time - $start_time" | bc)
    echo "Test $i: ${response_time}s"
    sleep 1
done

echo "✅ 모니터링 완료"
```

### 3. 로그 분석 도구

#### 에러 패턴 분석
```python
#!/usr/bin/env python3
"""
서버 로그 분석 스크립트
"""

import re
from collections import Counter
from datetime import datetime

def analyze_logs(log_file="server.log"):
    """서버 로그 분석"""
    
    error_patterns = []
    request_counts = Counter()
    response_times = []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # 에러 패턴 추출
                if 'ERROR' in line or 'EXCEPTION' in line:
                    error_patterns.append(line.strip())
                
                # API 요청 카운트
                if 'POST /api/' in line or 'GET /api/' in line:
                    match = re.search(r'(GET|POST) (/api/[^\s]+)', line)
                    if match:
                        request_counts[match.group(2)] += 1
                
                # 응답 시간 (FastAPI 로그에서)
                time_match = re.search(r'(\d+\.\d+)ms', line)
                if time_match:
                    response_times.append(float(time_match.group(1)))
    
    except FileNotFoundError:
        print(f"❌ 로그 파일을 찾을 수 없습니다: {log_file}")
        return
    
    # 분석 결과 출력
    print(f"📊 로그 분석 결과 ({log_file})")
    print("=" * 50)
    
    if error_patterns:
        print(f"\n❌ 에러 패턴 ({len(error_patterns)}개):")
        for error in error_patterns[-5:]:  # 최근 5개만
            print(f"  {error}")
    
    if request_counts:
        print(f"\n📈 API 요청 통계:")
        for endpoint, count in request_counts.most_common(5):
            print(f"  {endpoint}: {count}회")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        print(f"\n⏱️ 응답 시간:")
        print(f"  평균: {avg_time:.2f}ms")
        print(f"  최대: {max_time:.2f}ms")
        print(f"  샘플 수: {len(response_times)}")

if __name__ == "__main__":
    analyze_logs()
```

## 🆘 긴급 복구 가이드

### 서버 완전 다운 시

1. **긴급 재시작**
   ```bash
   #!/bin/bash
   # emergency_restart.sh
   
   echo "🚨 긴급 서버 재시작..."
   
   # 기존 프로세스 종료
   pkill -f "python.*server.py"
   sleep 2
   
   # 포트 정리
   fuser -k 8000/tcp 2>/dev/null
   
   # 가상환경 활성화 및 서버 시작
   cd /Users/user/loop/loop_ai
   source venv/bin/activate
   nohup python src/inference/server.py > server.log 2>&1 &
   
   # 헬스체크
   sleep 5
   if curl -s http://localhost:8000/api/health > /dev/null; then
       echo "✅ 서버 복구 성공"
   else
       echo "❌ 서버 복구 실패"
   fi
   ```

2. **설정 초기화**
   ```bash
   # 캐시 정리
   rm -rf __pycache__/ src/**/__pycache__/
   
   # 의존성 재설치
   pip install -r requirements.txt
   
   # 모델 재다운로드 (필요시)
   python scripts/download_qwen_models.py
   ```

---

**관련 문서:**
- [메인 API 문서](./README.md)
- [Fantasy Name Generator API](./fantasy-names.md)
- [Story Generator API](./story-generator.md)
- [사용 예제](./examples.md)

**추가 지원:**
- 실시간 로그 모니터링: `tail -f server.log`
- 인터랙티브 API 문서: http://localhost:8000/api/docs
- 건강 상태 확인: http://localhost:8000/api/health 