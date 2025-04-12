.PHONY: all clean

all: build/.imported

build/output.tsv: build/input.json export_tsv.py
	python3 export_tsv.py

clean:
	rm -rf build

build/input.json:
	@mkdir -p build
	@if [ -z "$$SCRAPBOX_PROJECT" ] || [ -z "$$SCRAPBOX_SESSION_ID" ]; then \
		echo "Error: SCRAPBOX_PROJECTとSCRAPBOX_SESSION_IDの環境変数を設定してください。"; \
		echo "例: export SCRAPBOX_PROJECT=your_project"; \
		echo "    export SCRAPBOX_SESSION_ID=xxxx"; \
		exit 1; \
	fi; \
	curl -s -H "Cookie: connect.sid=$$SCRAPBOX_SESSION_ID" "https://scrapbox.io/api/page-data/export/$$SCRAPBOX_PROJECT.json" -o build/input.json

build/.imported: build/output.tsv import_to_anki_upsert.py
	python3 import_to_anki_upsert.py
	touch build/.imported
