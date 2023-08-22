all: Overview.html IFTB.html

Overview.html: Overview.bs feature-registry.html
	bikeshed spec Overview.bs

IFTB.html: IFTB.bs
	bikeshed spec RangeRequest.bs

feature-registry.html: feature-registry.csv registry_to_html.py
	python3 registry_to_html.py > feature-registry.html

clean:
	rm Overview.html IFTB.html feature-registry.html
