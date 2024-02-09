all: Overview.html

Overview.html: Overview.bs
	bikeshed spec Overview.bs

feature-registry.html: feature-registry.csv registry_to_html.py
	python3 registry_to_html.py > feature-registry.html

clean:
	rm Overview.html RangeRequest.html feature-registry.html
