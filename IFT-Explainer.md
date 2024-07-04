# Incremental Font Transfer, Explained

## Author

- Chris Lilley, W3C

## Participate

- [IFT Issue tracker](https://github.com/w3c/IFT/issues)
- [IFT Specification](https://w3c.github.io/IFT/Overview.html)

## Table of Contents

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Motivating Use Cases](#motivating-use-cases)
- [Non-goals](#non-goals)
- [Considered alternatives](#considered-alternatives)
  - [Range Request](#range-request)
  - [Patch Subset](#patch-subset)
- [Incremental Font Transfer](#incremental-font-transfer)
- [Demo](#demo)
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
but when combined with CSS `unicode-range` is known to sometimes produce malformed, illegible text.

Static subsetting [fails](https://www.w3.org/TR/PFE-evaluation/#fail-subset) when there are
complex inter-relationships between different OpenType™ tables,
or when characters are **shared between multiple writing systems** but
behave **differently** in each one.

Current subsetting does not address subsetting **design axes** (variable fonts).

## Non-goals

Changes to the Open Font Format or OpenType specifications are out of scope.

## Considered alternatives

A 2020 [Evaluation Report](https://www.w3.org/TR/PFE-evaluation/)
simulated performance with two strategies: Range Request and Patch Subset.

Performance was simulated on
[**different speeds of network**](https://www.w3.org/TR/PFE-evaluation/#network)
(from fast wired to 2G),
for [**three classes of writing system**](https://www.w3.org/TR/PFE-evaluation/#langtype)
(simple alphabetic, complex shaping, and large)
and for two methods (Range Request and Patch Subset, see below).

Both **size** (total bytes transferred, including overhead)
and **network cost** (impact of latency on time to render)
were considered.

These initial approaches informed the current specification,
but the WG ended up discarding one and substantially rewriting the other.

### Range Request

The Range Request method relied on the existing HTTP Range Request functionality
and therefore could be used with **any HTTP server**.
For best efficiency, the font needed to be 
[re-ordered](https://w3c.github.io/IFT/RangeRequest.html#font-organization)
before upload to the server.

The client still needed to be updated to support this method.

Work on Range Request was discontinued because:

- Performance was insufficient in general
- Only glyph outlines were subsetted
- On slower networks, Range Request was [worse then no subsetting at all](https://www.w3.org/TR/PFE-evaluation/#conclusions-shaping)

### Patch Subset

The Patch Subset method required the server to 
[**dynamically respond to a PatchRequest**](https://www.w3.org/TR/2023/WD-IFT-20230530/#handling-patch-request)
by validating the request,
computing a binary patch between the current, subsetted font on the client
and the desired subset of the original font,
and then sending the patch,
which the client applied to produce a new, enlarged subset font.

It therefore required new server capabilities,
in addition to client changes.

Work on Patch Subset was discontinued because, despite
[median byte reductions of 90% for large fonts](https://www.w3.org/TR/PFE-evaluation/#analysis-cjk),

- The dynamic subsetting severely impacted CDN **cache performance**
- Subsetting fonts with **complex interactions between glyphs** was challenging
- Requiring an intelligent, dynamic server hindered widespread deployment
- Very fine-grained subsetting [might be a privacy violation](https://www.w3.org/TR/2023/WD-IFT-20230530/#content-inference-from-character-set)
- It required a custom protocol (and HTTP header) to communicate with the dynamic backend

## Incremental Font Transfer

The [current specification](https://w3c.github.io/IFT/Overview.html) 
draws on the Patch Subset concept
of patching a font to provide more data.
However, instead of requiring custom patch generation for each user,
the initial font has two new [_Patch Map_ tables](https://w3c.github.io/IFT/Overview.html#patch-map-dfn)
which map each subset definition to **the link** of the relevant patch.
Links are [stored in the font](https://w3c.github.io/IFT/Overview.html#uri-templates) 
as RFC 6570 [URI Templates](https://www.rfc-editor.org/rfc/rfc6570).

Thus, static hosting of files (base fonts, and patches) is easy,
and cache performance is good
because patches are shared between users.

We incorporated a new idea to allow patches of glyph-only data to be **independent**.
(This type of patch would have been too costly to compute dynamically, but they work well with this new framework of pre-computed patches.)

Thus, both **independent** (commutative) and **dependent** (non-commutative)
patches are [supported](https://w3c.github.io/IFT/Overview.html#font-format-extensions).

In addition, patches can add or extend design axes,
to support variable fonts.

It no longer requires any special HTTP headers,
or a custom protocol to fetch patches.
Requests are just normal HTTP GET requests,
making it easier to deploy and working well
with existing CDN infrastructure.

The main trade-off with this new approach is that
the patches potentially become less granular,
somewhat reducing peak efficiency,
while also being more privacy-preserving.

## Demo

We have a [proof of concept demo](https://garretrieger.github.io/ift-demo/) of the new IFT approach.

## Testing

We will work on tests;
the specification marks up each testable assertion.

 - [IFT client test suite](https://github.com/w3c/ift-client-tests) ([not yet](https://github.com/w3c/IFT/issues/125))

## Stakeholder Feedback / Opposition

- Chromium : Positive
- WebKit : No signals
- Gecko : No signals
- Font Vendors (Adobe, Apple, Dalton Maag, Google) : Positive
