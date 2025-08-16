## 1.30.3 - 2025-08-15
### Extractors
#### Additions
- [booth] add support ([#7920](https://github.com/mikf/gallery-dl/issues/7920))
- [civitai] add `collection` & `user-collections` extractors ([#8005](https://github.com/mikf/gallery-dl/issues/8005))
- [facebook] add `info` extractor ([#6582](https://github.com/mikf/gallery-dl/issues/6582))
- [facebook] add `albums` extractor ([#7848](https://github.com/mikf/gallery-dl/issues/7848))
- [imgdrive] add `image` extractor ([#7976](https://github.com/mikf/gallery-dl/issues/7976))
- [imgtaxi] add `image` extractor ([#8019](https://github.com/mikf/gallery-dl/issues/8019))
- [imgwallet] add `image` extractor ([#8021](https://github.com/mikf/gallery-dl/issues/8021))
- [picstate] add `image` extractor ([#7946](https://github.com/mikf/gallery-dl/issues/7946))
- [silverpic] add `image` extractor ([#8020](https://github.com/mikf/gallery-dl/issues/8020))
- [tumblr] add `following` & `followers` extractors ([#8018](https://github.com/mikf/gallery-dl/issues/8018))
- [xasiat] add support ([#4161](https://github.com/mikf/gallery-dl/issues/4161) [#5929](https://github.com/mikf/gallery-dl/issues/5929) [#7934](https://github.com/mikf/gallery-dl/issues/7934))
#### Fixes
- [blogger] fix video extraction ([#7892](https://github.com/mikf/gallery-dl/issues/7892))
- [comick] handle chapters without chapter data ([#7972](https://github.com/mikf/gallery-dl/issues/7972))
- [comick] handle volume-only chapters ([#8043](https://github.com/mikf/gallery-dl/issues/8043))
- [comick] fix exception when filtering by translation group ([#8045](https://github.com/mikf/gallery-dl/issues/8045))
- [deviantart:tiptap] fix `KeyError: 'attrs'` ([#7929](https://github.com/mikf/gallery-dl/issues/7929))
- [everia] fix image extraction ([#7973](https://github.com/mikf/gallery-dl/issues/7973) [#7977](https://github.com/mikf/gallery-dl/issues/7977))
- [facebook] fix `avatar` extraction for empty profiles ([#7962](https://github.com/mikf/gallery-dl/issues/7962))
- [facebook] handle profiles without photos or `set_id` ([#7962](https://github.com/mikf/gallery-dl/issues/7962))
- [fappic] rewrite thumbnail URLs ([#8013](https://github.com/mikf/gallery-dl/issues/8013))
- [idolcomplex] update to new domain and interface ([#7559](https://github.com/mikf/gallery-dl/issues/7559) [#8009](https://github.com/mikf/gallery-dl/issues/8009))
- [kemono][coomer] fix extraction ([#8028](https://github.com/mikf/gallery-dl/issues/8028) [#8031](https://github.com/mikf/gallery-dl/issues/8031))
- [kemono] update `/creators` endpoint ([#8039](https://github.com/mikf/gallery-dl/issues/8039) [#8040](https://github.com/mikf/gallery-dl/issues/8040))
- [kemono] don't set error status for posts without comments ([#7961](https://github.com/mikf/gallery-dl/issues/7961))
- [pixiv] fix `IndexError` for unviewable works ([#7940](https://github.com/mikf/gallery-dl/issues/7940))
- [pixiv] fix artworks downloads when using expired cookies ([#7987](https://github.com/mikf/gallery-dl/issues/7987))
- [scrolller] fix NSFW subreddit pagination ([#7945](https://github.com/mikf/gallery-dl/issues/7945))
- [twitter] fix potential `UnboundLocalError` when `videos` are disabled ([#7932](https://github.com/mikf/gallery-dl/issues/7932))
- [vsco] disable TLS 1.2 cipher suites by default ([#7984](https://github.com/mikf/gallery-dl/issues/7984) [#7986](https://github.com/mikf/gallery-dl/issues/7986))
- [wikimedia:wiki] fix `AttributeError: 'subcategories'` ([#7931](https://github.com/mikf/gallery-dl/issues/7931))
#### Improvements
- [aibooru] support `general.aibooru.online` & `aibooru.download`
- [comick] add `lang` option ([#7938](https://github.com/mikf/gallery-dl/issues/7938))
- [hentaifoundry] add `descriptions` option ([#7952](https://github.com/mikf/gallery-dl/issues/7952))
- [facebook] raise `AuthRequired` for profiles requiring cookies ([#7962](https://github.com/mikf/gallery-dl/issues/7962))
- [instagram] warn about lower quality image downloads ([#7921](https://github.com/mikf/gallery-dl/issues/7921))
- [kemono] support `"endpoint": "posts+"` for full metadata ([#8028](https://github.com/mikf/gallery-dl/issues/8028))
- [misskey] support `misskey.art` ([#7923](https://github.com/mikf/gallery-dl/issues/7923))
- [motherless] detect `404`/`File not found` pages
- [pixiv] detect suspended/deleted accounts ([#7990](https://github.com/mikf/gallery-dl/issues/7990))
- [pixiv] improve API error messages
- [pixiv] remove redundant cookies initialization code
- [scrolller] limit `title` length in default filenames
- [skeb] implement `include` option ([#6558](https://github.com/mikf/gallery-dl/issues/6558) [#7267](https://github.com/mikf/gallery-dl/issues/7267))
- [vk] update default `archive_fmt` ([#8030](https://github.com/mikf/gallery-dl/issues/8030))
#### Metadata
- [cien] provide `author[id]` metadata ([#6582](https://github.com/mikf/gallery-dl/issues/6582))
- [dankefuerslesen] extract more metadata ([#7915](https://github.com/mikf/gallery-dl/issues/7915))
- [dankefuerslesen:manga] fix metadata being overwritten
- [facebook] ensure numeric `user_id` values ([#7953](https://github.com/mikf/gallery-dl/issues/7953))
- [facebook:set] fix/improve `user_id` extraction ([#7848](https://github.com/mikf/gallery-dl/issues/7848))
- [fappic] fix `filename` values
#### Common
- [common] implement `"user-agent": "@BROWSER"` ([#7947](https://github.com/mikf/gallery-dl/issues/7947))
- [common] improve error message for non-Netscape cookie files ([#8014](https://github.com/mikf/gallery-dl/issues/8014))
### Downloaders
- [ytdl] don't overwrite existing `filename` data ([#7964](https://github.com/mikf/gallery-dl/issues/7964))
### Miscellaneous
- [docs/configuration] improve `client-id` & `api-key` instructions
- [docs/formatting] update and improve
- [job] apply `extension-map` to `SimulationJob` results ([#7954](https://github.com/mikf/gallery-dl/issues/7954))
- [job] improve URL `scheme` extraction performance
- [job] split collected DataJob results
- [path] implement `path-convert` option ([#493](https://github.com/mikf/gallery-dl/issues/493) [#6582](https://github.com/mikf/gallery-dl/issues/6582))
- [scripts] improve and extend `init`, `generate_test_result`, and `pyprint`
- extend `-A`/`--abort` & `"skip": "abort"` functionality ([#7891](https://github.com/mikf/gallery-dl/issues/7891))
- use more f-strings ([#7671](https://github.com/mikf/gallery-dl/issues/7671))
