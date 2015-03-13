# Introduction #

An extension namespace needs to go through a number of stages before being supported. This page tracks requested namespaces along with the necessary next steps.

# Stages #

## Spec ##
An extension requires a stable, clear public specification. It should answer any questions about what is and isn't valid.

## Test cases ##
Test cases are concrete sample documents that demonstrate valid or invalid behaviour along with a description of what the validator's conclusion should be. See
[the existing extension tests](http://feedvalidator.org/testcases/ext/) for examples.

## Patch ##
Code is written to ensure the tests pass. It needs to agree with their conclusions without making any of the existing tests fail. If it's supplied as a patch to the current development code it will be easy to merge.

# Details #

| **Request** | **Namespace** | **Spec** | **Test cases** | **Patch** | **Deployed?** |
|:------------|:--------------|:---------|:---------------|:----------|:--------------|
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/d9875d1b5313de65 | http://pipes.yahoo.com |  |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/3166770db9a1ed0e | http://www.adobe.com/amp/1.0 |  |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/05c7fded6f80132e | http://www.colorfulsoftware.com/projects/atomsphere/extension/sort/1.0 |  |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/97e734aa138904f3 | http://prismstandard.org/namespaces/basic/2.0/ | http://www.prismstandard.org/specifications/2.1/ |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/fe61f0ec215807e8 | http://zeevee.com/zinc/2009 | http://www.zeevee.com/zinc/developers/rssspec |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/19edda993fbf5e33 | http://xmlns.transmission.cc/ | http://wiki.transmission.cc/upload/b/b4/Tx_metadata_standard_1.0.pdf |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/a246aef345b067b0 | http://www.brightcove.tv/link |  |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/361d4d6042148cd2# | http://base.google.com/ns/1.0 http://base.google.com/cns/1.0 |  |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/1d8996c8f579b82f | http://a9.com/-/opensearch/extensions/relevance/1.0/ | http://www.opensearch.org/Specifications/OpenSearch/Extensions/Relevance/1.0/Draft_1 |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/a94a53b0a5af04c6 | http://gdata.youtube.com/schemas/2007 |  |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/8197567fc04f97e7 http://groups.google.com/group/feedvalidator-users/browse_thread/thread/422ce4fd7f986fa1 http://groups.google.com/group/feedvalidator-users/browse_thread/thread/f4402016311a7e41 | http://schemas.google.com/g/2005 |  |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/481cf8cb60dd7833 | http://api.maps.yahoo.com/Maps/V1/AnnotatedMaps.xsd |  |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/82d6d7c5a7b2244 | http://developer.longtailvideo.com/trac/wiki/FlashFormats | http://developer.longtailvideo.com/trac/wiki/Player5Formats#JWPlayerNamespace |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/dab8a72e730c2abb/04313459cd69223f | http://www.andymatuschak.org/xml-namespaces/sparkle | http://sparkle.andymatuschak.org/documentation/pmwiki.php/Documentation/PublishingAnUpdate |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/2f04e95b8cb957b7/057195fe6e8883fe | http://boxee.tv/spec/rss/ | http://developer.boxee.tv/rss.html |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/2a73b617b79ca278/ab95f2e4de2eac72 | http://www.itunesu.com/feed |  |  |  |  |
| http://groups.google.com/group/feedvalidator-users/browse_thread/thread/4a4620d22bd7a15d | http://api.twitter.com |  |  |  |  |