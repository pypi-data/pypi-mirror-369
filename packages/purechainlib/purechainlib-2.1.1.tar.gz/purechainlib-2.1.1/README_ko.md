<div align="left">
  
  # PureChain Python 라이브러리

  [![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Version](https://img.shields.io/badge/version-2.0.9-green)](https://pypi.org/project/purechainlib/)

  **가스 비용 제로 블록체인 개발을 위한 Python SDK**

  **완전히 무료한 트랜잭션**을 제공하는 PureChain EVM 네트워크용 Python SDK입니다. 가스 수수료 없이 스마트 컨트랙트 배포, 토큰 전송, 스마트 컨트랙트 상호작용이 가능합니다!
</div>

## 🆕 v2.1.0의 새로운 기능

### 🔒 스마트 컨트랙트 보안 감사 (신규!)
- **내장 보안 도구** - Slither & Mythril이 SDK에 포함됨
- **자동 설치** - 첫 사용 시 도구가 자동으로 설치됨
- **한 줄 감사** - `await pcl.audit("컨트랙트 코드")`
- **다중 도구** - Slither, Mythril 선택 또는 모두 실행
- **종합적인 로깅** - LLM 통합에 완벽
- **보고서 내보내기** - JSON, Markdown, HTML 형식

### 📚 문서 업데이트
- 비공개 GitHub 저장소 링크 제거
- 한국어 문서 접근 방법 개선
- 패키지에 영어와 한국어 문서 모두 포함
<!-- - 종합적인 도움말 시스템 추가 (힌트: `pc.help.`를 시도해보고 탐색해보세요!) -->

## 이전 업데이트 (v2.0.8)

### 🌍 한국어 지원
- 한국어 문서 및 가이드 제공
- 한국 개발자를 위한 최적화된 예제 코드
- PyPI에서 한국어 문서 다운로드 가능

### 🌱 탄소 발자국 추적
- 에너지 소비(줄) 및 CO2 배출량의 **과학적 측정**
- 환경 영향에 대한 **ESG 규정 준수** 보고
- **지역별 그리드 강도** 지원 (미국, EU, 아시아 등)
- 다른 블록체인과의 효율성 비교 (이더리움보다 99.99999% 적은 CO2!)

### 🔧 자동 Web3 미들웨어
- 더 이상 수동 `web3.middleware` 임포트 필요 없음
- 모든 Web3 버전과 자동 호환
- `from purechainlib import PureChain`만으로 준비 완료!

### 📊 에너지 측정
- 트랜잭션당 **0.029 줄** (과학적으로 측정됨)
- 비트코인보다 **630억 배** 더 효율적
- 추정치가 아닌 실제 CPU 전력 모니터링 기반

## 🚀 빠른 시작

```bash
pip install purechainlib
```

**참고:** 버전 2.0.9+는 Web3 미들웨어 구성을 자동으로 처리합니다. 수동 임포트나 패치가 필요 없습니다!

```python
import asyncio
from purechainlib import PureChain
# web3.middleware 임포트 불필요 - 자동으로 처리됨!

async def main():
    # PureChain 초기화
    pc = PureChain('testnet')
    
    # 지갑 연결
    pc.connect('여기에_개인키_입력')
    
    # 잔액 확인 (무료!)
    balance = await pc.balance()
    print(f"잔액: {balance} PURE")
    
    # 컨트랙트 배포 (무료!)
    contract_source = """
    pragma solidity ^0.8.19;
    contract Hello {
        string public message = "안녕하세요 PureChain!";
        function setMessage(string memory _msg) public {
            message = _msg;
        }
    }
    """
    
    factory = await pc.contract(contract_source)
    contract = await factory.deploy()  # 가스 수수료 없음!
    print(f"컨트랙트 배포됨: {contract.address}")

asyncio.run(main())
```

## ✨ 주요 기능

- **가스 비용 제로** - 모든 작업이 완전 무료
- **보안 감사** - 내장된 스마트 컨트랙트 취약점 스캔
- **사용하기 쉬움** - 간단하고 직관적인 API
- **완전한 EVM 지원** - 모든 Solidity 컨트랙트 배포 가능
- **Python다운 코드** - 깔끔하고 읽기 쉬운 Python 코드
- **보안** - 업계 표준 암호화
- **완벽한 기능** - 계정 관리, 컴파일, 배포, 감사 포함

## 📚 빠른 참조

### 모든 사용 가능한 함수

| 함수 | 설명 | 예제 |
|----------|-------------|---------|
| `PureChain(network, private_key?)` | 연결 초기화 | `pc = PureChain('testnet')` |
| `connect(private_key)` | 지갑 연결 | `pc.connect('개인키')` |
| `account()` | 새 계정 생성 | `acc = pc.account()` |
| `balance(address?)` | 잔액 조회 | `bal = await pc.balance()` |
| `bal(address?)` | 잔액 조회 (축약형) | `bal = await pc.bal()` |
| `send(to, value?)` | PURE 토큰 전송 | `await pc.send('0x...', '1.0')` |
| `contract(source)` | 컨트랙트 컴파일 | `factory = await pc.contract(code)` |
| `factory.deploy(*args)` | 컨트랙트 배포 | `contract = await factory.deploy()` |
| `call(contract, method, *args)` | 컨트랙트 읽기 | `result = await pc.call(contract, 'balances', addr)` |
| `execute(contract, method, *args)` | 컨트랙트 쓰기 | `await pc.execute(contract, 'mint', 1000)` |
| `block(number?)` | 블록 정보 조회 | `block = await pc.block()` |
| `transaction(hash)` | 트랜잭션 조회 | `tx = await pc.transaction('0x...')` |
| `gasPrice()` | 가스 가격 조회 (항상 0) | `price = await pc.gasPrice()` |
| `address(addr?)` | 주소 정보 조회 | `info = await pc.address()` |
| `isContract(address)` | 컨트랙트 여부 확인 | `is_contract = await pc.isContract('0x...')` |
| `events(contract, blocks?)` | 컨트랙트 이벤트 조회 | `events = await pc.events(addr, 10)` |
| `status()` | 네트워크 상태 조회 | `status = await pc.status()` |
| `tx(hash?)` | 트랜잭션 조회 (별칭) | `tx = await pc.tx('0x...')` |
| `testTPS(duration?, target?, mode?)` | TPS 성능 테스트 | `results = await pc.testTPS(30, 100, 'full')` |
| `measureLatency(operations?)` | 작업 지연시간 측정 | `latency = await pc.measureLatency(100)` |
| `benchmarkThroughput(duration?)` | 블록체인 처리량 테스트 (TPS) | `throughput = await pc.benchmarkThroughput(60)` |
| `runPerformanceTest(quick?)` | 전체 성능 테스트 | `results = await pc.runPerformanceTest()` |
| `enableCarbonTracking(region?)` | 탄소 발자국 추적 활성화 | `pc.enableCarbonTracking('asia')` |
| `disableCarbonTracking()` | 탄소 추적 비활성화 | `pc.disableCarbonTracking()` |
| `getCarbonReport()` | 탄소 배출 보고서 조회 | `report = await pc.getCarbonReport()` |
| `getCarbonESGMetrics()` | ESG 규정 준수 지표 조회 | `esg = await pc.getCarbonESGMetrics()` |
| `exportCarbonReport()` | 전체 탄소 보고서 JSON으로 내보내기 | `json_report = await pc.exportCarbonReport()` |
| **보안 감사** | | |
| `audit(contract, **kwargs)` | 한 줄 보안 감사 | `await pc.audit(code)` |
| `auditContract(contract, tool?)` | 전체 보안 감사 | `await pc.auditContract(code, tool=SecurityTool.SLITHER)` |
| `auditAndDeploy(contract, ...)` | 감사 후 안전하면 배포 | `await pc.auditAndDeploy(code, require_pass=True)` |
| `runSecurityLoop(contract, max?)` | 반복적 보안 수정 | `await pc.runSecurityLoop(code, max_iterations=5)` |
| `enableAutoAudit(tool?)` | 배포 전 자동 감사 | `pc.enableAutoAudit()` |
| `checkSecurityTools()` | 설치된 도구 확인 | `pc.checkSecurityTools()` |
| `getSecurityLogs()` | 모든 감사 로그 조회 | `logs = pc.getSecurityLogs()` |

### 함수 카테고리

#### 🔐 **계정 및 지갑 관리**
```python
# 초기화 및 연결
pc = PureChain('testnet', '선택적_개인키')
pc.connect('0x_없이_개인키_입력')

# 새 계정 생성
new_account = pc.account()
# 반환: {'address': '0x...', 'privateKey': '...'}

# 현재 서명자 주소 조회
address = pc.signer.address
```

#### 💰 **잔액 및 트랜잭션**
```python
# 잔액 확인
my_balance = await pc.balance()           # 내 잔액
other_balance = await pc.balance('0x...')  # 특정 주소
quick_balance = await pc.bal()            # 축약형

# PURE 토큰 전송 (무료!)
await pc.send('0x...수신자', '10.5')

# 트랜잭션 객체로 전송
await pc.send({
    'to': '0x...주소',
    'value': '1.0',
    'data': '0x...'  # 선택사항
})
```

#### 📄 **스마트 컨트랙트**
```python
# 컴파일 및 배포
contract_source = "pragma solidity ^0.8.19; contract Test { ... }"
factory = await pc.contract(contract_source)
deployed_contract = await factory.deploy(생성자_인자)

# 기존 컨트랙트에 연결
existing_contract = factory.attach('0x...컨트랙트_주소')

# 컨트랙트 읽기 (view 함수)
result = await pc.call(contract, 'balances', user_address)
name = await pc.call(contract, 'name')  # 인자 없음

# 컨트랙트 쓰기 (트랜잭션 함수)
await pc.execute(contract, 'mint', recipient, 1000)
await pc.execute(contract, 'setMessage', "안녕하세요!")
```

#### 🔍 **블록체인 정보**
```python
# 블록 정보
latest_block = await pc.block()           # 최신 블록
specific_block = await pc.block(12345)    # 특정 블록 번호

# 트랜잭션 정보
tx_info = await pc.transaction('0x...해시')
tx_alias = await pc.tx('0x...해시')      # 위와 동일

# 주소 정보
addr_info = await pc.address()           # 내 주소 정보
other_info = await pc.address('0x...')   # 특정 주소
# 반환: {'balance': '...', 'isContract': bool, 'address': '...'}

# 주소가 컨트랙트인지 확인
is_contract = await pc.isContract('0x...주소')

# 가스 가격 (PureChain에서는 항상 0)
gas_price = await pc.gasPrice()  # 0 반환

# 네트워크 상태
status = await pc.status()
# 반환: {'chainId': 900520900520, 'gasPrice': 0, 'blockNumber': ...}
```

#### 📊 **이벤트 및 모니터링**
```python
# 컨트랙트 이벤트 조회
events = await pc.events(contract_address)      # 모든 이벤트
recent_events = await pc.events(contract_address, 10)  # 최근 10블록
```

#### ⚡ **성능 테스트**
```python
# 다양한 측정 모드로 초당 트랜잭션 수(TPS) 테스트
# 모드 옵션: 'full' (기본값), 'send', 'parallel'
tps_full = await pc.testTPS(duration=30, target_tps=100, measure_mode='full')  # 전체 수명주기 측정
tps_send = await pc.testTPS(duration=30, target_tps=100, measure_mode='send')  # 전송 시간만 측정
tps_parallel = await pc.testTPS(duration=30, target_tps=100, measure_mode='parallel')  # 병렬 실행

print(f"전체 모드 TPS: {tps_full['actual_tps']}")
print(f"전송 전용 TPS: {tps_send['actual_tps']}")
print(f"병렬 TPS: {tps_parallel['actual_tps']}")

# 작업 지연시간 측정
latency_results = await pc.measureLatency(operations=100)
print(f"평균 지연시간: {latency_results['balance_check']['avg_ms']}ms")

# 블록체인 처리량 벤치마크 (혼합 작업 TPS)
throughput_results = await pc.benchmarkThroughput(test_duration=60)
print(f"처리량: {throughput_results['throughput_tps']} TPS")

# 전체 성능 테스트 실행
performance = await pc.runPerformanceTest(quick=True)  # 빠른 테스트
full_performance = await pc.runPerformanceTest(quick=False)  # 전체 테스트
```

## 📚 상세 API 레퍼런스

### 초기화

```python
from purechainlib import PureChain

# 테스트넷 연결 (기본값)
pc = PureChain('testnet')

# 또는 메인넷
pc = PureChain('mainnet')

# 개인키로 즉시 연결
pc = PureChain('testnet', '개인키')
```

### 계정 관리

```python
# 지갑 연결
pc.connect('0x_접두사_없이_개인키')

# 새 계정 생성
account = pc.account()
print(f"주소: {account['address']}")
print(f"개인키: {account['privateKey']}")

# 잔액 확인
balance = await pc.balance()  # 내 잔액
balance = await pc.balance('0x...주소')  # 특정 주소
```

### 컨트랙트 작업

```python
# 소스에서 컨트랙트 배포
contract_source = """
pragma solidity ^0.8.19;
contract Token {
    mapping(address => uint256) public balances;
    
    function mint(uint256 amount) public {
        balances[msg.sender] += amount;
    }
}
"""

# 컴파일 및 배포 (무료!)
factory = await pc.contract(contract_source)
contract = await factory.deploy()

# 컨트랙트 읽기 (무료!)
balance = await pc.call(contract, 'balances', user_address)

# 컨트랙트 쓰기 (무료!)
await pc.execute(contract, 'mint', 1000)
```

### 트랜잭션

```python
# PURE 토큰 전송 (무료!)
await pc.send('0x...수신자_주소', '10.5')

# 트랜잭션 객체로 전송
await pc.send({
    'to': '0x...주소',
    'value': '1.0',
    'data': '0x...'  # 선택적 컨트랙트 데이터
})
```

### 블록체인 정보

```python
# 최신 블록 조회
block = await pc.block()
print(f"블록 #{block['number']}")

# 트랜잭션 정보 조회
tx = await pc.transaction('0x...트랜잭션_해시')

# 네트워크 상태
status = await pc.status()
print(f"체인 ID: {status['chainId']}")
print(f"가스 가격: {status['gasPrice']}") # 항상 0!

# 가스 가격 (항상 0 반환)
gas_price = await pc.gasPrice()
```

### Python 스타일 단축키

```python
# 빠른 잔액 확인
balance = await pc.bal()

# 주소 정보
info = await pc.address()
print(f"잔액: {info['balance']}")
print(f"컨트랙트 여부: {info['isContract']}")

# 주소가 컨트랙트인지 확인
is_contract = await pc.isContract('0x...주소')
```

## 📝 완전한 예제

### 토큰 컨트랙트 배포 및 상호작용

```python
import asyncio
from purechainlib import PureChain

async def token_example():
    pc = PureChain('testnet')
    pc.connect('개인키')
    
    # 토큰 컨트랙트
    token_source = """
    pragma solidity ^0.8.19;
    
    contract SimpleToken {
        mapping(address => uint256) public balances;
        uint256 public totalSupply;
        string public name = "PureToken";
        
        function mint(address to, uint256 amount) public {
            balances[to] += amount;
            totalSupply += amount;
        }
        
        function transfer(address to, uint256 amount) public {
            require(balances[msg.sender] >= amount);
            balances[msg.sender] -= amount;
            balances[to] += amount;
        }
    }
    """
    
    # 토큰 배포 (무료!)
    factory = await pc.contract(token_source)
    token = await factory.deploy()
    print(f"토큰이 배포됨: {token.address}")
    
    # 토큰 발행 (무료!)
    await pc.execute(token, 'mint', pc.signer.address, 1000000)
    
    # 잔액 확인 (무료!)
    balance = await pc.call(token, 'balances', pc.signer.address)
    print(f"토큰 잔액: {balance}")
    
    # 토큰 전송 (무료!)
    recipient = "0xc8bfbC0C75C0111f7cAdB1DF4E0BC3bC45078f9d"
    await pc.execute(token, 'transfer', recipient, 100)
    print("토큰이 전송됨!")

asyncio.run(token_example())
```

### 여러 계정 생성 및 자금 제공

```python
import asyncio
from purechainlib import PureChain

async def multi_account_example():
    pc = PureChain('testnet')
    pc.connect('개인키')
    
    # 3개의 새 계정 생성
    accounts = []
    for i in range(3):
        account = pc.account()
        accounts.append(account)
        print(f"계정 {i+1}: {account['address']}")
    
    # 각 계정에 자금 제공 (무료 트랜잭션!)
    for i, account in enumerate(accounts):
        await pc.send(account['address'], f"{i+1}.0")  # 1, 2, 3 PURE 전송
        print(f"계정 {i+1}에 {i+1} PURE 전송됨")
    
    # 모든 잔액 확인
    for i, account in enumerate(accounts):
        balance = await pc.balance(account['address'])
        print(f"계정 {i+1} 잔액: {balance} PURE")

asyncio.run(multi_account_example())
```

### 컨트랙트 이벤트 모니터링

```python
import asyncio
from purechainlib import PureChain

async def event_example():
    pc = PureChain('testnet')
    pc.connect('개인키')
    
    # 이벤트가 있는 컨트랙트
    contract_source = """
    pragma solidity ^0.8.19;
    
    contract EventExample {
        event MessageSet(address indexed user, string message);
        
        string public message;
        
        function setMessage(string memory _message) public {
            message = _message;
            emit MessageSet(msg.sender, _message);
        }
    }
    """
    
    # 배포 및 상호작용
    factory = await pc.contract(contract_source)
    contract = await factory.deploy()
    
    # 메시지 설정 (이벤트 생성)
    await pc.execute(contract, 'setMessage', "안녕하세요 이벤트!")
    
    # 최근 10블록의 이벤트 조회
    events = await pc.events(contract.address, 10)
    print(f"{len(events)}개의 이벤트 발견")

asyncio.run(event_example())
```

### 성능 테스트 및 벤치마킹

```python
import asyncio
from purechainlib import PureChain

async def performance_testing():
    pc = PureChain('testnet')
    pc.connect('개인키')
    
    print("🚀 성능 테스트 시작...")
    
    # 1. TPS (초당 트랜잭션 수) 테스트
    print("\n1️⃣ TPS 테스트 - 트랜잭션 처리량 측정")
    tps_results = await pc.testTPS(duration=30, target_tps=50)
    
    print(f"목표 TPS: {tps_results['target_tps']}")
    print(f"달성 TPS: {tps_results['actual_tps']}")
    print(f"효율성: {tps_results['efficiency']}%")
    print(f"평균 지연시간: {tps_results['avg_latency_ms']}ms")
    
    # 2. 지연시간 테스트 - 작업 응답 시간 측정
    print(f"\n2️⃣ 지연시간 테스트 - 응답 시간 측정")
    latency_results = await pc.measureLatency(operations=50)
    
    for operation, stats in latency_results.items():
        print(f"{operation}: {stats['avg_ms']}ms (최소: {stats['min_ms']}, 최대: {stats['max_ms']})")
    
    # 3. 처리량 테스트 - 데이터 전송률 측정
    print(f"\n3️⃣ 처리량 테스트 - 데이터 전송 측정")
    throughput_results = await pc.benchmarkThroughput(test_duration=45)
    
    print(f"총 TPS: {throughput_results['throughput_tps']}")
    print(f"데이터 전송: {throughput_results['kb_per_second']} KB/s")
    print(f"성공률: {throughput_results['success_rate']}%")
    
    # 4. 전체 성능 테스트
    print(f"\n4️⃣ 전체 성능 테스트")
    full_results = await pc.runPerformanceTest(quick=False)
    
    print(f"📊 성능 요약:")
    print(f"네트워크: {full_results['network']['networkName']}")
    print(f"블록: #{full_results['network']['blockNumber']}")
    print(f"지연시간: {full_results['latency']['balance_check']['avg_ms']}ms")
    print(f"TPS: {full_results['tps']['actual_tps']}")
    print(f"처리량: {full_results['throughput']['throughput_tps']} TPS")

asyncio.run(performance_testing())
```

### 빠른 성능 확인

```python
import asyncio
from purechainlib import PureChain

async def quick_performance_check():
    pc = PureChain('testnet')
    pc.connect('개인키')
    
    # 빠른 15초 테스트
    results = await pc.runPerformanceTest(quick=True)
    
    print("⚡ 빠른 성능 결과:")
    print(f"TPS: {results['tps']['actual_tps']}")
    print(f"지연시간: {results['latency']['balance_check']['avg_ms']}ms")
    print(f"처리량: {results['throughput']['throughput_tps']} TPS")

asyncio.run(quick_performance_check())
```

## 🌐 네트워크 정보

| 네트워크 | RPC URL | 체인 ID | 가스 가격 |
|---------|---------|----------|-----------|
| **테스트넷** | `https://purechainnode.com:8547` | `900520900520` | `0` (무료!) |
| **메인넷** | `https://purechainnode.com:8547` | `900520900520` | `0` (무료!) |

## ⚡ 성능 지표 가이드

### 성능 결과 이해하기

성능 테스트를 실행할 때 각 지표의 의미:

#### 🚀 **TPS (초당 트랜잭션 수)**
- **목표 TPS**: 달성하고자 하는 속도
- **실제 TPS**: PureChain이 실제로 제공한 속도
- **효율성**: 목표에 얼마나 근접했는지 (%)
- **측정 모드**:
  - **`full`**: 완전한 트랜잭션 수명주기 측정 (전송 + 확인 대기)
  - **`send`**: 전송 시간만 측정 (확인 대기 안 함)
  - **`parallel`**: 동시에 트랜잭션 전송 및 두 단계 모두 측정

**시간 분석:**
- **전송 시간**: 트랜잭션 구성, 서명, 네트워크 브로드캐스트 시간
- **확인 시간**: 브로드캐스트부터 채굴/확인까지 시간
- **총 지연시간**: 전송 시간 + 확인 시간

```python
# TPS 결과 예시
{
    'duration': 30.0,
    'successful_transactions': 1487,
    'failed_transactions': 0,
    'actual_tps': 49.57,
    'target_tps': 50,
    'efficiency': 99.14,
    'avg_latency_ms': 523.2,
    'contract_address': '0x...'
}
```

#### 📊 **지연시간 측정**
- **잔액 확인**: 계정 잔액 조회 시간
- **블록 가져오기**: 최신 블록 정보 조회 시간
- **컨트랙트 호출**: 스마트 컨트랙트 읽기 시간
- **트랜잭션 전송**: 전송 및 확인 시간

```python
# 지연시간 결과 예시
{
    'balance_check': {'avg_ms': 21.45, 'min_ms': 12.3, 'max_ms': 45.2},
    'block_fetch': {'avg_ms': 19.8, 'min_ms': 11.1, 'max_ms': 38.9},
    'contract_call': {'avg_ms': 23.1, 'min_ms': 14.5, 'max_ms': 52.3},
    'transaction_send': {'avg_ms': 487.3, 'min_ms': 234.1, 'max_ms': 892.1}
}
```

#### ⚡ **처리량 지표**
- **처리량 TPS**: 초당 혼합 작업 수 (쓰기 + 읽기)
- **쓰기 TPS**: 초당 쓰기 트랜잭션 수
- **읽기 TPS**: 초당 읽기 작업 수
- **데이터 전송**: 초당 KB 단위 데이터 이동량
- **성공률**: 성공적으로 완료된 작업 비율

### 성능 최적화 모범 사례

#### 🎯 **애플리케이션 최적화**

```python
# 1. 가능한 경우 작업 일괄 처리
async def batch_operations():
    pc = PureChain('testnet')
    pc.connect('개인키')
    
    # 여러 개별 호출 대신
    # for user in users:
    #     balance = await pc.balance(user)
    
    # 동시 실행 사용
    import asyncio
    balances = await asyncio.gather(*[
        pc.balance(user) for user in users
    ])

# 2. 읽기 작업 효율적으로 사용
async def efficient_reads():
    pc = PureChain('testnet')
    
    # 자주 액세스하는 데이터 캐시
    latest_block = await pc.block()
    
    # 여러 쿼리에 블록 번호 사용
    for contract in contracts:
        # 캐시된 블록 데이터로 처리
        pass

# 3. 프로덕션에서 성능 모니터링
async def production_monitoring():
    pc = PureChain('mainnet')
    pc.connect('프로덕션_키')
    
    # 주기적으로 빠른 성능 확인 실행
    health_check = await pc.runPerformanceTest(quick=True)
    
    if health_check['tps']['actual_tps'] < 20:
        # 경고: 성능 저하 감지
        send_alert("PureChain 성능이 임계값 이하")
```

### 성능 테스트 팁

```python
# 1. 먼저 네트워크 워밍업
async def performance_with_warmup():
    pc = PureChain('testnet')
    pc.connect('개인키')
    
    # 워밍업 - 먼저 몇 개의 트랜잭션 전송
    print("🔥 네트워크 워밍업 중...")
    for _ in range(5):
        await pc.balance()
    
    # 이제 실제 성능 테스트 실행
    results = await pc.testTPS(30, 50)

# 2. 다른 시간대 테스트
# 네트워크 성능은 사용량에 따라 달라질 수 있음

# 3. 메인넷 vs 테스트넷 비교
testnet_results = await PureChain('testnet').runPerformanceTest()
mainnet_results = await PureChain('mainnet').runPerformanceTest()

# 4. 시간 경과에 따른 모니터링
performance_history = []
for day in range(7):
    daily_results = await pc.runPerformanceTest(quick=True)
    performance_history.append(daily_results)
```

## 🌱 탄소 발자국 추적

PureChain SDK는 **탄소 발자국 추적** 기능을 포함합니다

### 왜 탄소 추적이 필요한가?

PureChain이 **가스 수수료 제로**를 사용하고 매우 효율적이지만, 모든 계산 작업은 여전히 환경에 영향을 미칩니다. 투명하고 과학적인 측정을 제공하여 다음을 도와드립니다:
- ESG 보고를 위한 환경 영향 추적
- 다른 블록체인과의 효율성 비교
- 블록체인 사용에 대한 정보에 입각한 결정
- 규정 준수 보고서 생성

### 탄소 추적 사용 방법

```python
# 지역별 탄소 추적 활성화
pc = PureChain('testnet')
pc.enableCarbonTracking('asia')  # 옵션: 'global', 'us', 'eu', 'asia', 'renewable'

# 탄소 데이터와 함께 트랜잭션 전송
result = await pc.send(address, amount, include_carbon=True)
print(f"탄소 발자국: {result['carbon_footprint']['carbon']['gCO2']} gCO2")

# 탄소 추적과 함께 컨트랙트 배포
contract = await factory.deploy(track_carbon=True)

# 탄소 보고서 조회
report = await pc.getCarbonReport()
print(f"총 배출량: {report['total_emissions']['kgCO2']} kg CO2")

# 보고를 위한 ESG 지표 조회
esg = await pc.getCarbonESGMetrics()
print(f"환경 지표: {esg['environmental']}")

# 전체 보고서 내보내기
json_report = await pc.exportCarbonReport()
```

### 🔬 과학적 방법론

우리의 탄소 계산은 추정치가 아닌 **실제 측정**을 기반으로 합니다:

#### 에너지 측정
- Intel PowerTOP 및 turbostat을 사용한 **직접 CPU 전력 모니터링**
- **측정 환경**: Intel Xeon E5-2686 v4 @ 2.30GHz (일반적인 클라우드 서버)
- **트랜잭션당 에너지**: ~0.029 줄 (8.1 × 10⁻⁹ kWh)
- **정확도**: 측정 분산에 따라 ±5%

#### 탄소 계산
```
탄소 (gCO2) = 에너지 (kWh) × 그리드 탄소 강도 (gCO2/kWh)
```

**그리드 탄소 강도 출처:**
- 미국: EPA eGRID 2023 (평균 420 gCO2/kWh)
- EU: EEA 2023 (평균 295 gCO2/kWh)
- 글로벌: IEA 2023 (평균 475 gCO2/kWh)

### 📊 측정된 성능

| 작업 | 에너지 (줄) | 탄소 (gCO2) | vs 이더리움 |
|-----------|-----------------|---------------|-------------|
| 트랜잭션 | 0.029 | 0.000003 | 99.99999% 적음 |
| 컨트랙트 배포 | 0.517 | 0.000054 | 99.9998% 적음 |
| 컨트랙트 실행 | 0.010 | 0.000001 | 99.99999% 적음 |

### 다른 블록체인과의 비교

```python
# PureChain 측정값 (트랜잭션당)
{
    'purechain': {
        'energy_kwh': 0.000000008,
        'co2_g': 0.000003,
        'comparison': '기준선'
    },
    'ethereum_pow': {
        'energy_kwh': 30,
        'co2_g': 30000,
        'times_worse': 3750000000  # 37.5억 배
    },
    'ethereum_pos': {
        'energy_kwh': 0.01,
        'co2_g': 10,
        'times_worse': 1250000  # 125만 배
    },
    'bitcoin': {
        'energy_kwh': 511,
        'co2_g': 500000,
        'times_worse': 63875000000  # 639억 배
    }
}
```

### 탄소 추적 API 레퍼런스

#### 추적 활성화/비활성화
```python
# 특정 지역으로 활성화
pc.enableCarbonTracking('us')  # 미국 그리드 강도
pc.enableCarbonTracking('eu')  # EU 그리드 강도
pc.enableCarbonTracking('renewable')  # 재생 에너지

# 추적 비활성화
pc.disableCarbonTracking()
```

#### 트랜잭션 탄소 데이터
```python
# 트랜잭션에 탄소 포함
result = await pc.send(to, value, include_carbon=True)

# 탄소 데이터 구조
{
    'carbon': {
        'gCO2': 0.000003,        # CO2 그램
        'kgCO2': 0.000000003,    # 킬로그램
        'tonnesCO2': 3e-12       # 미터톤
    },
    'comparison': {
        'vs_ethereum': '0.00001%',
        'savings_kg': 30.0
    },
    'environmental': {
        'trees_equivalent': 0.0000001
    },
    'offset': {
        'cost_usd': 0.00000003
    }
}
```

#### ESG 보고

```python
# ESG 준수 지표 조회
esg = await pc.getCarbonESGMetrics()

# 반환값
{
    'environmental': {
        'total_emissions_kg_co2': 0.000001,
        'emissions_per_transaction_g_co2': 0.000003,
        'carbon_efficiency_vs_ethereum': '99.99%+ 감소',
        'renewable_energy_compatible': True
    },
    'sustainability': {
        'zero_gas_operations': True,
        'energy_efficient': True
    },
    'reporting': {
        'methodology': 'ISO 14064-1 호환',
        'verification': 'PureChain SDK로 자동 추적'
    }
}
```

### 🌍 환경 영향

이더리움 대신 PureChain을 사용하여 1,000개의 트랜잭션을 처리하면:
- **에너지**: 30 kWh 절약 (가정 1일 전력량)
- **탄소**: 30 kg CO2 절약 (연간 1.4그루의 나무)
- **비용**: $3.60 전기료 절약

### 참고문헌

1. Sedlmeir et al. (2020): "The Energy Consumption of Blockchain Technology"
2. Cambridge Bitcoin Electricity Consumption Index (2023)
3. EPA eGRID Power Profiler (2023)
4. IEA Global Energy & CO2 Status Report (2023)

## 🔒 보안 감사 기능

PureChainLib에는 스마트 컨트랙트 보안 감사 도구가 내장되어 있습니다. Slither, Mythril, Manticore, Solhint 등 업계 표준 도구를 SDK 내에서 직접 사용할 수 있습니다.

### 빠른 시작 (한 줄 코드)

```python
import purechainlib as pcl

# 가장 간단한 보안 감사 - 한 줄!
result = await pcl.audit("contract MyToken { ... }")
```

### 보안 도구 자동 설치

첫 사용 시 필요한 보안 도구가 자동으로 설치됩니다:

```python
# CLI에서 수동 설치
purechainlib-security-setup

# 또는 Python에서
from purechainlib.security_setup import SecuritySetup
SecuritySetup.check_and_install_tools()
```

### Pythonic 사용 예제

#### 1. 기본 감사 (Slither)

```python
import purechainlib as pcl

# 한 줄로 감사 실행
audit_result = await pcl.audit("""
    pragma solidity ^0.8.0;
    contract VulnerableContract {
        mapping(address => uint256) balances;
        
        function withdraw() public {
            uint256 amount = balances[msg.sender];
            (bool success, ) = msg.sender.call{value: amount}("");
            balances[msg.sender] = 0;  // 재진입 취약점!
        }
    }
""")

print(f"발견된 문제: {audit_result['issues_count']}")
for issue in audit_result['issues']:
    print(f"- {issue['severity']}: {issue['title']}")
```

#### 2. 다양한 도구로 감사

```python
# Mythril로 심층 분석
mythril_result = await pcl.audit(contract_code, tool="mythril")

# Manticore로 형식 검증
manticore_result = await pcl.audit(contract_code, tool="manticore")

# Solhint로 코드 스타일 검사
solhint_result = await pcl.audit(contract_code, tool="solhint")
```

#### 3. PureChain 인스턴스로 감사

```python
pc = PureChain('testnet')

# 기본 감사
result = await pc.audit(contract_source)

# 특정 도구 사용
result = await pc.audit(contract_source, tool="mythril")

# 모든 도구로 종합 감사
result = await pc.auditWithAllTools(contract_source)
print(f"총 {len(result)} 개 도구로 감사 완료")
```

#### 4. 감사 후 자동 배포 (안전한 경우만)

```python
# 감사 통과 시에만 배포
contract = await pc.auditAndDeploy(
    contract_source,
    require_pass=True  # 심각한 문제 발견 시 배포 중단
)

if contract:
    print(f"✅ 안전한 컨트랙트 배포됨: {contract.address}")
else:
    print("❌ 보안 문제로 배포 취소됨")
```

#### 5. LLM과 통합한 자동 수정 루프

```python
async def secure_contract_with_llm(contract_code, llm_client):
    """LLM을 사용한 자동 보안 개선"""
    
    pc = PureChain('testnet')
    max_iterations = 3
    
    for i in range(max_iterations):
        # 감사 실행
        audit = await pc.audit(contract_code)
        
        if audit['severity_counts']['high'] == 0:
            print(f"✅ 반복 {i+1}: 안전한 컨트랙트!")
            return contract_code
            
        # LLM에게 수정 요청
        fixed_code = await llm_client.fix_vulnerabilities(
            contract_code, 
            audit['issues']
        )
        
        contract_code = fixed_code
        print(f"🔧 반복 {i+1}: {audit['issues_count']}개 문제 수정 시도")
    
    return contract_code
```

### 지원 도구 및 기능

| 도구 | 용도 | 강점 |
|------|------|------|
| **Slither** | 정적 분석 | 빠른 속도, 정확한 탐지 |
| **Mythril** | 기호 실행 | 심층 취약점 분석 |
| **Manticore** | 형식 검증 | 복잡한 논리 검증 |
| **Solhint** | 린터 | 코드 스타일 및 모범 사례 |

## ❓ 자주 묻는 질문

**Q: 트랜잭션이 정말 무료인가요?**  
A: 네! PureChain은 가스 비용이 제로입니다. 모든 작업이 0 PURE입니다.

**Q: 모든 Solidity 컨트랙트를 배포할 수 있나요?**  
A: 네! PureChain은 완전한 EVM 호환성을 제공합니다.

**Q: Web3와 호환되나요?**  
A: 네! Web3.py 기반으로 PureChain 전용 최적화가 포함되어 있습니다.

## 🔗 링크

- **NPM 패키지**: https://www.npmjs.com/package/purechainlib
- **PyPI 패키지**: https://pypi.org/project/purechainlib/
- **한국어 문서**: 패키지 설치 시 README_ko.md 파일 포함

## 📄 라이선스

MIT 라이선스 - 모든 프로젝트에서 자유롭게 사용 가능!

---

**가스 제로. 완전한 EVM. 순수한 혁신.** 🚀

*블록체인 개발 비용이 전혀 들지 않는 PureChain 생태계를 위해 제작되었습니다!*