Портация бибилиотеки crest для Bitrix24
===========

Пример вызова:

    from b24rest import BitrixCrest
    bx = BitrixCrest()
    bx.call('telephony.externalcall.hide', {
        'CALL_ID': '',
        'USER_ID': ',
    })

