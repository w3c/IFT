all: Overview.html

Overview.html: Overview.bs
	bikeshed spec Overview.bs

clean:
	rm Overview.html RangeRequest.html
