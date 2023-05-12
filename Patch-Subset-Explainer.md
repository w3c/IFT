# Patch Subset method for Incremental Font Transfer, Explained

## Author

- Chris Lilley, W3C

## Participate

- [IFT Issue tracker](https://github.com/w3c/IFT/issues)
- [IFT Patch-Subset Specification](https://w3c.github.io/IFT/Overview.html)
- [IFT Range Request Specification](https://w3c.github.io/IFT/RangeRequest.html)

## Table of Contents

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Motivating Use Cases](#motivating-use-cases)
- [Non-goals](#non-goals)
- [Evaluation Report](#evaluation-report)
- [Range Request vs. Patch Subset](#range-request-vs-patch-subset)
- [Detailed design discussion](#detailed-design-discussion)
  - [Why use two methods](#why-use-two-methods)
  - [Why use a url query parameter](#why-use-a-url-query-parameter)
  - [Privacy concern: snooping on the user](#privacy-concern-snooping-on-the-user)
- [Testing](#testing)
- [Stakeholder Feedback / Opposition](#stakeholder-feedback--opposition)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

Web Fonts allow web pages to download and use **fonts on demand**,
without the fonts needing to be **installed**.

Incremental transfer allows clients to load
only the **portions of the font** they actually need
which speeds up font loads and reduces data transfer needed to load the fonts.
A font can be loaded over **multiple requests**
where each request incrementally adds additional data.

## Motivating Use Cases

WebFont usage is _high globally_, around [**75%**](https://almanac.httparchive.org/en/2022/fonts#fig-1) of top-level web pages use it.

However, WebFonts are currently primarily used with **simple writing systems** such as [Latin, Greek and Cyrillic](https://almanac.httparchive.org/en/2022/fonts#writing-system-and-languages)
where the median WOFF2 size is [**8.3kB**](https://www.w3.org/TR/PFE-evaluation/#font-langtype)

For fonts with _many glyphs_ (such as are typically used for Chinese and Japanese, for example),
even with the compression provided by WOFF 1 or 2,
download sizes are still **far too large**
with a median WOFF2 size of [**1.8MB**](https://www.w3.org/TR/PFE-evaluation/#font-langtype).
Thus, usage of Web Fonts in China and Japan is [**close to zero**](https://www.w3.org/TR/PFE-evaluation/#fail-large).

For languages with a small set of glyphs, **static font subsetting** is widely deployed.

However, for those languages with **complex shaping requirements**,
static subsetting gives small files (median WOFF2 size of [**93.5kB**](https://www.w3.org/TR/PFE-evaluation/#font-langtype))
but is known to sometimes produce malformed, illegible text.

Static subsetting [fails](https://www.w3.org/TR/PFE-evaluation/#fail-subset) when there are
complex inter-relationships between different OpenType™ tables,
or when characters are **shared between multiple writing systems** but
behave **differently** in each one.

## Non-goals

Changes to the Open Font Format or OpenType specifications are out of scope.

## Evaluation Report

A 2020 [Evaluation Report](https://www.w3.org/TR/PFE-evaluation/) simulated and 
evaluates solutions which would allow WebFonts to be used
where slow networks, very large fonts,
or complex subsetting requirements currently preclude their use.

_Note: At that time, the technology was called Progressive Font Enrichment (PFE)._
_The name has since been changed to Incremental Font Transfer (IFT)._

Performance was simulated on
[**different speeds of network**](https://www.w3.org/TR/PFE-evaluation/#network)
(from fast wired to 2G),
for [**three classes of writing system**](https://www.w3.org/TR/PFE-evaluation/#langtype)
(simple alphabetic, complex shaping, and large)
and for two methods (Range Request and Patch Subset, see below).

Both **size** (total bytes transferred, including overhead)
and **network cost** (impact of latency on time to render)
were considered.

## Range Request vs. Patch Subset

The Patch Subset method requires the server to 
[**respond to a PatchRequest**](https://w3c.github.io/IFT/Overview.html#handling-patch-request)
by validating the request,
computing a binary patch between the current, subsetted font on the client
and the desired subset of the original font,
and then sending the patch,
which the client applies to produce a new, enlarged subset font.

It therefore requires new server capabilities,
in addition to client changes.

The Range Request method relies on the existing HTTP Range Request functionality
and therefore can be used with **any HTTP server**.
For best efficiency, the font should be [re-ordered](https://w3c.github.io/IFT/RangeRequest.html#font-organization)
before upload to the server.
The client still needs to be updated to support this method.

Self-hosting of fonts [**remains popular**](https://almanac.httparchive.org/en/2022/fonts#fig-3) and is **likely to grow** due to privacy concerns over centralized hosting services.
Thus, a method that does not require a specialized server is attractive.
At the same time,
a method that **offers no benefit** or
[**makes performance much worse**](https://www.w3.org/TR/PFE-evaluation/#analysis-cjk-cost)
is of no use, regardless of ease of deployment.

Thus the [IFT specification](https://w3c.github.io/IFT/Overview.html) (and this explainer)
focusses on the Patch Subset method,
and gives a way to [**negotiate a method**](https://w3c.github.io/IFT/Overview.html#method-selection).

Progress on the Range Request method is slower,
with [more issues](https://github.com/w3c/IFT/issues?q=is%3Aissue+is%3Aopen+label%3A%22Range+Request%22),
and it is currently in a [separate specification](https://w3c.github.io/IFT/RangeRequest.html).

## Detailed design discussion

### Why use two methods

Early review by the IETF HTTP WG raised a question of why we need two different methods, why not just **pick the best one**. The main issues raised were:

 - [Why do we have two methods](https://github.com/w3c/IFT/issues/120)
 - [Explain more clearly why we have two methods and what the trade-offs are.](https://github.com/w3c/IFT/issues/104)

As a result the spec now [clearly explains](https://w3c.github.io/IFT/Overview.html#performance-considerations) the benefits and trade-offs. The issues were closed to the satisfaction of the commenter.

The **overhead** of doing [method negotiation](https://w3c.github.io/IFT/Overview.html#method-negotiation) was also discussed:

 - [Method negotiation has potential time wastes in it](https://github.com/w3c/IFT/issues/30)

We were able to eliminate that overhead by removing the uneeded PatchRequest message,
 when initiating a range request session.

### Why use a url query parameter

The FPWD used url queries, because we wanted to avoid multiple round trips
before getting the font data,
and because on first request the client doesn't know
which methods the server supports.
This requires sending some binary data.

It was seen as problematic by the HTTP WG, because it impinges on a
[server's authority over its own URLs](https://www.rfc-editor.org/rfc/rfc8820.html).

 - [Query parameters](https://github.com/w3c/IFT/issues/75)
 - [Negotiation algorithm is not ideal](https://github.com/w3c/IFT/issues/107)

The HTTP WG introduced us the HTTP [QUERY](https://httpwg.org/http-extensions/draft-ietf-httpbis-safe-method-w-body.html),
which seemed like a better way to achieve the same result.
There is an open issue, as QUERY is still a draft wil limited real-world deployment:

 - [Add QUERY as a HTTP method type used for patch subset.](https://github.com/w3c/IFT/issues/127)

We solved this by firstly introducing three
[CSS `font-tech` keywords](https://drafts.csswg.org/css-fonts-4/#font-tech-definitions): 
incremental-patch, incremental-range and incremental-auto.
Secondly, by using a [Font-Patch-Request](https://w3c.github.io/IFT/Overview.html#patch-request-header) 
HTTP header for the initial request
(thus avoiding the overhead of a CORS preflight request).
The binary data is compactly encoded in CBOR.
Subsequent requests can use HTTP POST.

These changes resolved the issues to the satisfaction of the commenters,
and we removed the query parameter.

### Privacy concern: snooping on the user

The Privacy IG raised a concern:

 - [Proposal would allow pages to learn how the user is interacting with the site](https://github.com/w3c/IFT/issues/50)

There was initially some confusion over terminology such as "third party",
and also perhaps a lack of appreciation that HTTPS (which is required for IFT)
prevents the person-in-the-middle attack,
or that information is required to [not leak across origins](https://w3c.github.io/IFT/Overview.html#per-origin).

- [Require that incrementally-loaded fonts not be preserved nor exposed to other origins](https://github.com/w3c/IFT/issues/43)

Discussion then centere around what an (assumed malicious)
IFT font server could **learn about the user**.
For example, in languages with very large character sets,
it might be possible to infer the type of content on the web page,
by looking for unusual characters whose use tends to be domain specific.

Discussion is ongoing, and the current state of our understanding
is in the specification as [Content inference from character set](https://w3c.github.io/IFT/Overview.html#content-inference-from-character-set).

## Testing

We are working on tests, even at this early stage;
the specification marks up each testable assertion.

 - [test suite for servers](https://github.com/w3c/ift-server-tests) (in progress)
 - [test suite for clients](https://github.com/w3c/ift-client-tests) ([not yet](https://github.com/w3c/IFT/issues/125))

## Stakeholder Feedback / Opposition

- Chromium : Positive
- WebKit : Positive
- Gecko : No signals
- Font Vendors (Adobe, Apple, Dalton Maag, Google) : Positive
