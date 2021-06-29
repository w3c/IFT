all: Overview.html RangeRequest.html

Overview.html: Overview.bs
	bikeshed spec Overview.bs

RangeRequest.html: RangeRequest.bs
	bikeshed spec RangeRequest.bs

clean:
	rm Overview.html RangeRequest.html
