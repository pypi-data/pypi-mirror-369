# src/my_awesome_bootstrapper/__init__.py

"""
py-init-bootstrap
-----------------
Create a fully-initialized Python project with a virtual environment and sensible defaults.
"""

# 1. cli 모듈의 main 함수를 패키지 최상단으로 끌어올립니다.
from .cli import main

# 2. 패키지 버전 정보를 명시합니다.
__version__ = "0.1.0"

# 3. 공개 API를 __all__에 정의합니다.
__all__ = ["main"]