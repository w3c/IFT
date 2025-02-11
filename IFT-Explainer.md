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
- [Incremental Font Transfer](#incremental-font-transfer)
- [Demo](#demo)
- [Testing](#testing)
- [Considered alternatives](#considered-alternatives)
  - [Range Request](#range-request)
  - [Patch Subset](#patch-subset)
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

## Incremental Font Transfer

Web pages that wish to use an IFT font
use the regular CSS [`@font-face`]() mechanism,
and [opt-in](https://w3c.github.io/IFT/Overview.html#opt-in)
with `tech(incremental)` or by using `font-tech(incremental)`
inside an `@supports` rule.
This allows the same CSS file to link to an IFT font
and to some (larger, slower) fallback font.

The link in the `src` descriptor points to an 
[IFT font](https://w3c.github.io/IFT/Overview.html),
which is a regular OpenType font;
this is commonly encoded as WOFF2 for efficient transfer.

It containins only the data needed to correctly render some
[subset](https://w3c.github.io/IFT/Overview.html#font-subset-dfn)
of:

- code points,
- layout features
- design-variation space

This subset also contains [extra tables](https://w3c.github.io/IFT/Overview.html#font-format-extensions)
which carry [patch maps](https://w3c.github.io/IFT/Overview.html#patch-map-dfn).
which map subset definitions to **the link** of the relevant patch.
Links are [stored in the font](https://w3c.github.io/IFT/Overview.html#uri-templates) 
as RFC 6570 [URI Templates](https://www.rfc-editor.org/rfc/rfc6570).

In contrast to static font subsets, 
these links allow [**font patches**](https://w3c.github.io/IFT/Overview.html#font-patch-definitions)
to be downloaded on demand
and applied to the initially downloaded font,
to support additional code points, layout features, or variation spaces.

For example, an IFT font might support only Latin characters,
with a single weight.
But the font also provides URLs for patches
that add a weight variation axis,
or add small caps,
or support Cyrillic characters.
These would be downloaded and applied on demand,
as content is encountered that needs them.

This avoids the rendering breakage often encountered with  _complex writing script languages_
such as Arabic and Indic languages,
when multiple static subsets are used together.

It also allows webfonts to be used for languages such as Chinese and Japanese,
because glyphs for additional codepoints are only downloaded
when they are actually needed.

In this architecture, static hosting of files (IFT fonts, and patches) is easy,
and **cache performance** is compatible
with existing CDN infrastructure
because patches are shared between users.
It is also also more **privacy-preserving**
(compared to other approaches which were considered, see below).

As a performance optimization, IFT allows patches for glyph-only data to be **independent**,
Meaning they can be requested in parallel,
which functionally is very similar to how unicode range webfont loading works.

Thus, both **independent** (commutative) and **dependent** (non-commutative)
patches are [supported](https://w3c.github.io/IFT/Overview.html#font-format-extensions).


## Demo

We have a [proof of concept demo](https://garretrieger.github.io/ift-demo/) of the new IFT approach.

## Testing

We will work on tests;
the specification marks up each testable assertion.

 - [IFT client test suite](https://github.com/w3c/ift-client-tests) ([not yet](https://github.com/w3c/IFT/issues/125))

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

## Stakeholder Feedback / Opposition

- Chromium : Positive. [Implementation](https://github.com/googlefonts/fontations/tree/main/incremental-font-transfer)
- WebKit : No signals. [Request for Position](https://github.com/WebKit/standards-positions/issues/461)
- Gecko : No signals. [Request for Position](https://github.com/mozilla/standards-positions/issues/872)
- Font Vendors (Adobe, Dalton Maag, Google) : Positive
