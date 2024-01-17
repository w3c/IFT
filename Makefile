all: Overview.html PatchSubset.html RangeRequest.html

Overview.html: Overview.bs
	bikeshed spec Overview.bs

PatchSubset.html: PatchSubset.bs feature-registry.html
	bikeshed spec PatchSubset.bs

RangeRequest.html: RangeRequest.bs
	bikeshed spec RangeRequest.bs

feature-registry.html: feature-registry.csv registry_to_html.py
	python3 registry_to_html.py > feature-registry.html

clean:
	rm Overview.html RangeRequest.html feature-registry.html
