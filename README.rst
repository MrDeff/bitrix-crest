** Портация бибилиотеки crest для Bitrix24
===========

**Использование

```
from b24rest import BitrixCrest
bx = BitrixCrest()
bx.call('telephony.externalcall.hide', {
    'CALL_ID': '',
    'USER_ID': ',
})
```