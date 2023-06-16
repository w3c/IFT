all: Overview.html RangeRequest.html

Overview.html: Overview.bs feature-registry.html
	bikeshed spec Overview.bs

RangeRequest.html: RangeRequest.bs
	bikeshed spec RangeRequest.bs

feature-registry.html: feature-registry.csv registry_to_html.py
	python3 registry_to_html.py > feature-registry.html

obfuscation-blocks.html: obfuscation_blocks_to_html.py
	python3 obfuscation_blocks_to_html.py > obfuscation-blocks.html

clean:
	rm Overview.html RangeRequest.html feature-registry.html
