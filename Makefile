all: Overview.html

Overview.html: Overview.bs feature-registry.html
	bikeshed spec Overview.bs

feature-registry.html: feature-registry.csv registry_to_html.py
	python3 registry_to_html.py > feature-registry.html

clean:
	rm -f Overview.html feature-registry.html
