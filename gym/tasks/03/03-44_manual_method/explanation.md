# Why this works

Send the supplied method envelope and return the server's response. Explain RPC failures versus business rejection.

The exercise uses real manual objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    response = await context["http"].post("/rpc", **context["arguments"])
    return response.json()
~~~
