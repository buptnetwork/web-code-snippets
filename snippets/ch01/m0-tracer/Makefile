.PHONY: seed run raw plain verify verify-all

seed:
	uv run python seed.py

run:
	uv run uvicorn v2_traceable:app --host 127.0.0.1 --port 8000

raw:
	uv run uvicorn v1_ai_raw:app --host 127.0.0.1 --port 8000

plain:
	TRACE_MODE=plain DEMO_DELAY_MS=80 uv run uvicorn v2_traceable:app --host 127.0.0.1 --port 8000

verify:
	uv run python verify_m0.py

verify-all:
	uv run python verify_m0.py --all
