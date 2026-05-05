
try:
    import jwt
    print("jwt: OK")
except ImportError:
    print("jwt: MISSING")

try:
    import httpx
    print("httpx: OK")
except ImportError:
    print("httpx: MISSING")

try:
    import backend.models.employability_predictor as ep
    print("employability_predictor: OK")
except Exception as e:
    print(f"employability_predictor: ERROR - {e}")
