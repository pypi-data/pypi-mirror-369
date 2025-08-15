def maybe_jit(func=None, **jit_kwargs):
    try:
        import numba  # type: ignore
    except Exception:
        # No numba available; return identity decorator or function
        if func is None:
            def deco(f):
                return f
            return deco
        return func
    # numba is available
    # Respect explicit request for object mode via nopython=False by mapping to forceobj=True
    if 'nopython' in jit_kwargs and jit_kwargs.get('nopython') is False:
        jit_kwargs = {k: v for k, v in jit_kwargs.items() if k != 'nopython'}
        jit_kwargs['forceobj'] = True
    if func is None:
        def deco(f):
            return numba.jit(**jit_kwargs)(f)  # type: ignore
        return deco
    return numba.jit(**jit_kwargs)(func)  # type: ignore
