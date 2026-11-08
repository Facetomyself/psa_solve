# Host API reads before clearance XHR

Pid 46624. Cutoff is the clearance XHR send, exclusive. No string values longer than 24 characters. String cells are length plus first codepoint.

## Clearance send

- Seq 97261, method POST, body length 8620 (class ~8000).
- Earlier send on the same pid is seq 2281, body length 2252. That one is not the cutoff.
- Later readyState 4 on this exchange is status 200, response length 3792. Form submit events are seq 100351-100354, after this send.
- Inventory window: get/call with seq < 97261. Counts: get 969, call 814, unique interface.member 171.

## Specific getters

| interface.member | count | value class | seq |
| --- | ---: | --- | --- |
| Window.innerWidth | 11 | [1920] | 83485-84171 |
| Window.innerHeight | 10 | [939] | 83481-83736 |
| Window.outerWidth | 0 | absent |  |
| Window.outerHeight | 0 | absent |  |
| Window.devicePixelRatio | 0 | absent |  |
| Window.screenX | 0 | absent |  |
| Window.screenY | 0 | absent |  |
| Screen.width | 0 | absent |  |
| Screen.height | 0 | absent |  |
| Screen.availWidth | 0 | absent |  |
| Screen.availHeight | 0 | absent |  |
| Screen.colorDepth | 0 | absent |  |
| Screen.pixelDepth | 0 | absent |  |
| Navigator.webdriver | 0 | absent |  |
| Navigator.hardwareConcurrency | 0 | absent |  |
| Navigator.deviceMemory | 0 | absent |  |
| Navigator.maxTouchPoints | 0 | absent |  |
| Navigator.cookieEnabled | 1 | [true] | 340-340 |
| Navigator.language | 0 | absent |  |
| Navigator.languages | 0 | absent |  |
| Navigator.platform | 0 | absent |  |
| Navigator.userAgent | 0 | absent |  |
| Navigator.vendor | 0 | absent |  |
| Navigator.pdfViewerEnabled | 0 | absent |  |
| Navigator.plugins | 0 | absent |  |
| Navigator.doNotTrack | 0 | absent |  |
| Navigator.productSub | 0 | absent |  |
| Document.hidden | 0 | absent |  |
| Document.visibilityState | 1 | str [{"len": 7, "cp": 118}] | 83483-83483 |
| Document.hasFocus | 0 | absent |  |
| Performance.now | 0 | absent |  |
| Date.now | 47 | [1790582187920, 1790582187922, 1790582187927, 1790582187928, 1790582187938, 1790582187960, 1790582188061, 1790582188591, 1790582188605, 1790582188606, 1790582188608, 1790582188611, 1790582188962, 1790582188963, 1790582188969, 1790582189155, 1790582189162, 1790582189718, 1790582189725, 1790582189749, 1790582190282, 1790582190288, 1790582190845, 1790582190851] | 66-84926 |

WebGL, WebGL2, canvas 2d, AudioContext, and OfflineAudioContext members: 0 gets/calls before the send. Performance.now: 0. Date.now: 47 (numeric timestamps; min seq 66). Adjacent, not WebGL: Navigator.gpu count 1, GPU.requestAdapter count 1.

Document.hidden count 0. Document.hasFocus count 0. Document.visibilityState count 1, string class len 7 cp 118 (short enum, visible). Navigator.cookieEnabled count 1, boolean true. No reads of webdriver, hardwareConcurrency, deviceMemory, maxTouchPoints, language, languages, platform, userAgent, vendor, pdfViewerEnabled, plugins, or doNotTrack.

Window.matchMedia count 1 (seq 83129). MediaQueryList.matches count 1, boolean false. Query class: length 28, first codepoint 40, feature token prefers-, no width or height numbers. Not a viewport-size read.

## Headed vs windowless 1920x1080 / screen 1366x768 / outerWidth 0

Claimed only where this trace actually contains the read.

- Window.innerHeight is 939 on all 10 reads (seq 83481-83736). A 1920x1080 viewport would report 1080. Difference evidenced.
- Window.innerWidth is 1920 on all 11 reads (seq 83485-84171). Same as the windowless viewport width. No difference.
- outerWidth, outerHeight, devicePixelRatio, screenX, screenY, and Screen.width/height/availWidth/availHeight/colorDepth/pixelDepth are not read before the send. No difference claimed for the 1366x768 screen or outerWidth 0.
- cookieEnabled true and visibilityState visible are not numeric mismatches against that geometry.

Best host surface to patch: Window.innerHeight. It is the only geometry API in this pre-send window whose number disagrees with a 1920x1080 viewport.

## Top 80 interface.member before seq 97261

| rank | count | interface.member | seq | return class |
| ---: | ---: | --- | --- | --- |
| 1 | 149 | Window.window | 3-84878 | object-or-empty |
| 2 | 115 | String.charCodeAt | 376-97260 | sample [13, 25, 35, 41, 48, 57, 69, 76, 77, 79, 85, 97] |
| 3 | 72 | RTCPeerConnectionIceEvent.candidate | 762-84458 | str [{"len": 24, "cp": 91}] |
| 4 | 64 | NodeList.length | 186-83866 | [0, 6, 47] |
| 5 | 62 | NodeIterator.nextNode | 83870-84061 | str [{"len": 13, "cp": 91}, {"len": 24, "cp": 91}, {"len": 25, "cp": 91}, {"len": 26, "cp": 91}] |
| 6 | 48 | Math.floor | 106-84686 | sample [0, 1, 2, 21, 26, 66, 75, 83, 90, 94, 109, 123] |
| 7 | 48 | RTCIceCandidate.candidate | 768-84461 | str [{"len": 78, "cp": 99}, {"len": 79, "cp": 99}, {"len": 86, "cp": 99}, {"len": 97, "cp": 99}] |
| 8 | 47 | Date.now | 66-84926 | sample [1790582187920, 1790582187922, 1790582187927, 1790582187928, 1790582187938, 1790582187960, 1790582188061, 1790582188591, 1790582188605, 1790582188606, 1790582188608, 1790582188611] |
| 9 | 45 | Element.tagName | 83774-84169 | str [{"len": 4, "cp": 72}, {"len": 4, "cp": 77}, {"len": 5, "cp": 83}, {"len": 5, "cp": 84}] |
| 10 | 44 | Window.document | 4-84702 | object-or-empty |
| 11 | 36 | Math.round | 83490-83725 | sample [0, 65, 68, 128, 160, 192, 244, 300, 304, 772, 842, 896] |
| 12 | 35 | Node.parentNode | 191-84620 | str [{"len": 23, "cp": 91}, {"len": 24, "cp": 91}, {"len": 25, "cp": 91}] |
| 13 | 34 | Map.get | 374-84693 | str [{"len": 9, "cp": 117}, {"len": 15, "cp": 91}, {"len": 49, "cp": 87}] |
| 14 | 32 | Document.createElement | 5-83338 | str [{"len": 25, "cp": 91}, {"len": 26, "cp": 91}, {"len": 27, "cp": 91}, {"len": 29, "cp": 91}] |
| 15 | 31 | HTMLElement.style | 300-84679 | object-or-empty |
| 16 | 27 | MessageEvent.data | 83393-84627 | str [{"len": 15, "cp": 91}] |
| 17 | 27 | Node.parentElement | 83478-84692 | str [{"len": 23, "cp": 91}, {"len": 24, "cp": 91}, {"len": 25, "cp": 91}] |
| 18 | 26 | Node.appendChild | 43-83345 | object-or-empty |
| 19 | 26 | Element.getAttribute | 83185-83220 | object-or-empty |
| 20 | 25 | Math.min | 23-83894 | [0, 2, 3, 24, 26, 41, 151, 256, 257, 577, 750] |
| 21 | 23 | Node.isConnected | 83477-84483 | [true] |
| 22 | 20 | Window.setTimeout | 60-84602 | sample [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14] |
| 23 | 20 | Element.classList | 154-84722 | object-or-empty |
| 24 | 20 | Map.has | 82957-84630 | [false, true] |
| 25 | 18 | PerformanceEntry.entryType | 101-83377 | str [{"len": 8, "cp": 114}, {"len": 10, "cp": 110}] |
| 26 | 18 | DOMTokenList.add | 155-83168 | str [{"len": 9, "cp": 117}] |
| 27 | 18 | Element.querySelector | 270-84676 | str [{"len": 23, "cp": 91}, {"len": 26, "cp": 91}] |
| 28 | 18 | HTMLIFrameElement.contentWindow | 605-84619 | object-or-empty |
| 29 | 18 | DocumentFragment.querySelector | 83403-84618 | str [{"len": 26, "cp": 91}] |
| 30 | 17 | BigInt.BigInt | 69-87 | str [{"len": 2, "cp": 48}, {"len": 2, "cp": 49}, {"len": 6, "cp": 54}, {"len": 310, "cp": 49}] |
| 31 | 16 | PerformanceResourceTiming.responseStart | 104-83382 | [0, 406.96, 582.24, 703.3, 726.44, 940.62, 1115.36] |
| 32 | 15 | Element.querySelectorAll | 185-315 | object-or-empty |
| 33 | 15 | Object.assign | 498-83222 | str [{"len": 15, "cp": 91}] |
| 34 | 14 | Math.max | 25-84687 | [2, 3, 12, 24, 41, 149, 255, 575, 748, 5397] |
| 35 | 14 | Function.toString | 552-84594 | str [{"len": 37, "cp": 102}, {"len": 38, "cp": 102}] |
| 36 | 13 | Window.location | 9-84181 | object-or-empty |
| 37 | 13 | JSON.parse | 145-84832 | [0] |
| 38 | 13 | Map.set | 387-84223 | str [{"len": 12, "cp": 91}] |
| 39 | 12 | EventTarget.addEventListener | 65-82987 | str [{"len": 9, "cp": 117}] |
| 40 | 11 | PerformanceEntry.name | 116-83390 | str [{"len": 35, "cp": 104}, {"len": 41, "cp": 104}, {"len": 99, "cp": 104}, {"len": 268, "cp": 104}] |
| 41 | 11 | Window.innerWidth | 83485-84171 | [1920] |
| 42 | 10 | Element.setAttribute | 215-83435 | str [{"len": 9, "cp": 117}] |
| 43 | 10 | Window.innerHeight | 83481-83736 | [939] |
| 44 | 10 | Element.getBoundingClientRect | 83488-84139 | str [{"len": 16, "cp": 91}] |
| 45 | 10 | DOMRectReadOnly.top | 83495-84140 | [0, 128, 304] |
| 46 | 9 | Document.body | 98-83843 | str [{"len": 24, "cp": 91}] |
| 47 | 9 | Document.querySelector | 148-84706 | str [{"len": 23, "cp": 91}, {"len": 25, "cp": 91}, {"len": 27, "cp": 91}, {"len": 29, "cp": 91}] |
| 48 | 9 | MessageEvent.isTrusted | 83392-84607 | [true] |
| 49 | 9 | MessageEvent.origin | 83400-84615 | str [{"len": 33, "cp": 104}] |
| 50 | 9 | MessageEvent.source | 83413-84628 | object-or-empty |
| 51 | 9 | DOMRect.height | 83489-83718 | [65, 67.69999694824219, 243.6999969482422, 772, 842] |
| 52 | 9 | DOMRect.width | 83491-83720 | [300, 896, 960, 1280] |
| 53 | 9 | DOMRectReadOnly.left | 83493-83722 | [0, 160, 192] |
| 54 | 9 | CSSStyleProperties.contentVisibility | 83504-83737 | str [{"len": 7, "cp": 118}] |
| 55 | 9 | CSSStyleProperties.display | 83505-83738 | str [{"len": 4, "cp": 102}, {"len": 4, "cp": 103}, {"len": 5, "cp": 98}, {"len": 6, "cp": 105}] |
| 56 | 9 | CSSStyleProperties.opacity | 83506-83739 | str [{"len": 1, "cp": 49}] |
| 57 | 9 | CSSStyleProperties.position | 83507-83740 | str [{"len": 6, "cp": 115}] |
| 58 | 9 | CSSStyleProperties.transform | 83508-83741 | str [{"len": 4, "cp": 110}] |
| 59 | 9 | CSSStyleProperties.visibility | 83509-83742 | str [{"len": 7, "cp": 118}] |
| 60 | 9 | Element.attributes | 83845-83965 | object-or-empty |
| 61 | 8 | PerformanceResourceTiming.requestStart | 105-83379 | [0, 331.4, 487.92, 620.2, 726.44, 849.7, 1005.72] |
| 62 | 8 | PerformanceResourceTiming.responseEnd | 107-83381 | [408.08, 648.52, 703.34, 752.92, 961.96, 1117.88, 1554.72] |
| 63 | 8 | PerformanceEntry.duration | 110-83384 | [0, 26.479999999999905, 123.13999999999999, 177.83999999999992, 190.24, 242.78000000000003, 423.22000000000014, 1727.38] |
| 64 | 8 | PerformanceResourceTiming.transferSize | 112-83386 | [0, 2534, 3683, 28396, 81235, 83242] |
| 65 | 8 | PerformanceResourceTiming.encodedBodySize | 114-83388 | [0, 2234, 3383, 28096, 80935, 82942] |
| 66 | 8 | Window.postMessage | 83446-84562 | str [{"len": 9, "cp": 117}] |
| 67 | 8 | Element.previousElementSibling | 84143-84168 | str [{"len": 23, "cp": 91}, {"len": 27, "cp": 91}, {"len": 29, "cp": 91}] |
| 68 | 7 | Location.href | 12-84182 | str [{"len": 41, "cp": 104}] |
| 69 | 7 | Math.random | 373-83244 | [0.11927092592515698, 0.3504582687335903, 0.4794133958979202, 0.5042480140172266, 0.5688839949329375, 0.5861356087683695, 0.8839997023899634] |
| 70 | 7 | Map.entries | 83180-84691 | str [{"len": 21, "cp": 91}] |
| 71 | 6 | Window.crypto | 61-334 | str [{"len": 15, "cp": 91}] |
| 72 | 6 | Node.insertBefore | 178-325 | object-or-empty |
| 73 | 6 | PerformanceObserverEntryList.getEntries | 735-83374 | str [{"len": 14, "cp": 91}] |
| 74 | 5 | Map.Map | 88-84221 | str [{"len": 12, "cp": 91}] |
| 75 | 5 | Window.top | 134-84180 | object-or-empty |
| 76 | 5 | Node.nextSibling | 192-324 | str [{"len": 20, "cp": 91}, {"len": 23, "cp": 91}] |
| 77 | 5 | Object.keys | 686-84222 | str [{"len": 14, "cp": 91}] |
| 78 | 5 | RegExp.test | 82972-83228 | [true] |
| 79 | 5 | Document.documentElement | 83576-83731 | str [{"len": 24, "cp": 91}] |
| 80 | 5 | Attr.name | 83847-83915 | str [{"len": 3, "cp": 100}, {"len": 4, "cp": 108}, {"len": 10, "cp": 104}] |

Ranks 81+ omitted (91 further interface.member keys).
