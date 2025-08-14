# 소개

**PyLogger**는 Python 애플리케이션에서 구조화된 로그를 남기고, Fluent Bit 등 외부 로깅 시스템으로 전송할 수 있도록 도와주는 로깅 유틸리티입니다.

# 실행

### 환경 변수 설정

**PyLogger**는 프로젝트 .env 파일에서 다음 값을 읽어옵니다. 사용하는 프로젝트의 루트 디렉토리에 반드시 아래 두 환경 변수를 .env 파일에 설정해야 합니다.

- `FLUENTBIT_URL`: 로그를 전송할 Fluent Bit의 URL
- `COMPONENT_NAME`: 로그에 출력할 서비스 이름 (e.g. `datatransfer` or `noti`)
- `SYSTEM_NAME`: 로그에 출력할 서비스 이름 (e.g. `aps`,`dp`, `common` or `cp`)

# 지원하는 로그 레벨 및 카테고리

### 로그 레벨 (level)

- `debug`
- `info`
- `warn`
- `error`
- `critical`

### 로그 카테고리 (category)

- `request`
- `response`
- `service`
- `outbound`
- `excel`
- `access`
- `query`

# 주요 메서드 설명

- `bind_base_info()`: 컴포넌트와 시스템 정보로 기본 로그 컨텍스트를 초기화합니다.
- `bind_request_properties(request)`: 요청 정보를 바탕으로 로그 컨텍스트에 요청 속성을 추가합니다. 이 메서드를 호출하면 요청 URL, 메서드, 클라이언트 정보, 헤더 (특히 `tenant-id`, `tenant-name`, `project-name`) 등이 로그 속성에 포함됩니다.
- `send_log(level, category, message)`: 지정된 로그 레벨(`level`), 카테고리(`category`), 메시지(`message`)로 로그를 남기고, 설정된 `FLUENTBIT_URL`로 로그 데이터를 전송합니다.
- `add_to_log(data: dict)`: 추가적인 로그 속성을 현재 로그 컨텍스트에 바인딩합니다. `data`는 키-값 쌍으로 이루어진 딕셔너리이며, 이후 `send_log`로 남기는 로그에 이 속성들이 함께 포함됩니다.

# 설치

### 필요한 패키지

- `loguru`
- `pydantic-settings`
- `requests`

### 설치 예시

1. `AleatorikUI-UI-Backend-Net` 디렉토리로 이동하세요.
2. `Poetry` 패키지 매니저 사용 시 프로젝트의 (e.g. DataTransfer, SmartReport) Poetry 가상환경을 활성화시키세요.
3. 다음 명령들을 실행하세요:

   ```bash
   cd pycommon
   poetry install --no--root
   ```

# 기본 사용법

### 1. 인스턴스 가져오기

```python
from pylogger.core import logger_instance
```

### 2. 로그 컨텍스트 바인딩

로그를 남기기 전에, 기본 정보와 HTTP 요청 정보를 바인딩해야 합니다. 먼저 `bind_base_info()`로 컴포넌트와 시스템 정보를 초기화한 후, `bind_request_properties(request)`로 요청 관련 속성을 추가합니다.

```python
from fastapi import Request  # 예시: FastAPI Request 객체

async def some_endpoint(request: Request):
    logger_instance.bind_base_info()
    logger_instance.bind_request_properties(request)
    # ... 로직 ...
```

`request`는 FastAPI, Flask 등에서 전달되는 HTTP 요청 객체여야 합니다.

### 3. 로그 보내기

로그를 남길 때는 `send_log` 메서드를 사용합니다.

```python
logger_instance.send_log(level="info", category="response", message="사용자가 로그인했습니다.")
```

# 커스텀 속성 추가

추가적인 정보를 로그에 포함하고 싶을 때는 `add_to_log`를 사용할 수 있습니다.

```python
@app.get("/items/{item_id}")
async def read_item(request: Request, item_id: int):
    logger_instance.add_to_log({"item_price": 20.5, "user_role": "guest"})
    logger_instance.send_log(level="info", category="request", message=f"아이템 {item_id} 조회 요청")
    return {"item_id": item_id}
```

# API 미들웨어 연동

**PyLogger**는 FastAPI 애플리케이션과 미들웨어를 통해 API 요청을 로깅하는 데 효과적으로 사용될 수 있습니다. 다음은 FastAPI 애플리케이션에 미들웨어를 적용하여 각 API 요청을 로깅하는 예시입니다.

```python
from fastapi import Request, Response, FastAPI
from starlette.background import BackgroundTask
from urllib.parse import urlparse
from pylogger.logger import logger_instance


def log_request(request: Request) -> None:
    """Helper function to log request details with consistent formatting."""
    # Message format: [Info] [Access] - <REQUEST PATH>
    log_msg = f"{urlparse(str(request.url)).path}"
    logger_instance.send_log(level="info", category="access", message=log_msg)


async def process_request(request: Request, call_next):
    """Middleware to log HTTP request and response using pylogger."""
    # Bypass logging for health check endpoints
    request_path = urlparse(str(request.url)).path
    if request_path.rstrip("/").endswith("/health"):
        return await call_next(request)

    logger_instance.bind_base_info()
    logger_instance.bind_request_properties(request)
    response = await call_next(request)
    request.state.status_code = response.status_code

    # Log in the background without delaying response
    task = BackgroundTask(log_request, request)

    res_body = b"".join([chunk async for chunk in response.body_iterator])
    return Response(
        content=res_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
        background=task
    )


def setup_logging_middleware(app: FastAPI):
    """Registers logging middleware in the FastAPI app."""
    app.middleware("http")(process_request)
```

위 예시에서 `process_request` 미들웨어는 각 요청에 대해 `log_request` 백그라운드 작업을 실행하여 요청 정보를 로깅합니다. `bind_base_info()`와 `bind_request_properties()`를 통해 로그 컨텍스트가 설정되어 로그에 필요한 기본 정보와 요청 정보가 포함됩니다.
