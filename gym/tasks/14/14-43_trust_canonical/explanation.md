# Why this works

Sign the reordered document. Exclude existing signatures and produce the same JCS signature.

The exercise uses real trust objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from common.security import sign_card

    document = dict(reversed(list(context["card"].items())))
    return sign_card(document, context["private"], context["kid"])
~~~
