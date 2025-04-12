.PHONY: all clean tsv

all: output.tsv

output.tsv: input.json export_tsv.py
	python3 export_tsv.py

clean:
	rm -f input.json output.tsv

input.json:
	@if [ -z "$$SCRAPBOX_PROJECT" ] || [ -z "$$SCRAPBOX_SESSION_ID" ]; then \
		echo "Error: SCRAPBOX_PROJECTとSCRAPBOX_SESSION_IDの環境変数を設定してください。"; \
		echo "例: export SCRAPBOX_PROJECT=your_project"; \
		echo "    export SCRAPBOX_SESSION_ID=xxxx"; \
		exit 1; \
	fi; \
	http https://scrapbox.io/api/page-data/export/$$SCRAPBOX_PROJECT.json Cookie:"connect.sid=$$SCRAPBOX_SESSION_ID" > input.json
