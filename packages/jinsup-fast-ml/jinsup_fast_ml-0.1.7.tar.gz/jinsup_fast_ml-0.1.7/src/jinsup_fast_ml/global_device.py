import torch
import torch.nn as nn
from torch.utils.data import DataLoader

# 전역 상태 
if torch.backends.mps.is_available():
    _DEVICE = torch.device("mps")
elif torch.cuda.is_available():
    _DEVICE = torch.device("cuda")
else:
    _DEVICE = torch.device("cpu")

_ORIG_DATALOADER_ITER = None
_ORIG_DATALOADER_INIT = None
_ORIG_MODULE_CALL = None
_ORIG_RANDOM_SPLIT = None
_ORIG_RANDPERM = None
_ORIG_RAND = None
_ORIG_RANDN = None
_ORIG_RANDINT = None
_ORIG_MULTINOMIAL = None


def _move(obj):
    if torch.is_tensor(obj):
        return obj.to(_DEVICE)
    elif isinstance(obj, (list, tuple)):
        return type(obj)(_move(o) for o in obj)
    elif isinstance(obj, dict):
        return {k: _move(v) for k, v in obj.items()}
    return obj

def _align_float_dtype(obj, target_dtype):
    """부동소수 텐서만 target_dtype로 캐스팅. 정수/불리언은 그대로."""
    if torch.is_tensor(obj):
        if obj.is_floating_point():
            return obj.to(dtype=target_dtype)
        return obj
    elif isinstance(obj, (list, tuple)):
        return type(obj)(_align_float_dtype(o, target_dtype) for o in obj)
    elif isinstance(obj, dict):
        return {k: _align_float_dtype(v, target_dtype) for k, v in obj.items()}
    return obj


def _coerce_generator(g):
    if g is None:
        ng = torch.Generator(device=_DEVICE)
        return ng
    if hasattr(g, "device") and g.device != _DEVICE:
        try:
            ng = torch.Generator(device=_DEVICE)
            ng.manual_seed(int(g.initial_seed()))
            return ng
        except Exception:
            return None
    return g

def _wrap_random(func):
    def wrapper(*args, **kwargs):
        g = kwargs.get("generator", None)
        g2 = _coerce_generator(g)
        if g2 is None and "generator" in kwargs:
            kwargs.pop("generator")
        else:
            kwargs["generator"] = g2
        if "device" in kwargs:
            kwargs["device"] = _DEVICE
        else:
            try:
                return func(*args, device=_DEVICE, **kwargs)
            except TypeError:
                pass
        return func(*args, **kwargs)
    return wrapper

def _patch():
    global _ORIG_DATALOADER_ITER, _ORIG_MODULE_CALL, _ORIG_RANDOM_SPLIT
    global _ORIG_RANDPERM, _ORIG_RAND, _ORIG_RANDN, _ORIG_RANDINT, _ORIG_MULTINOMIAL
    global _ORIG_DATALOADER_INIT

    torch.set_default_device(_DEVICE)

    if _ORIG_DATALOADER_ITER is None:
        _ORIG_DATALOADER_ITER = DataLoader.__iter__
        def _patched_iter(self):
            for batch in _ORIG_DATALOADER_ITER(self):
                yield _move(batch)
        DataLoader.__iter__ = _patched_iter

    if _ORIG_DATALOADER_INIT is None:
        _ORIG_DATALOADER_INIT = DataLoader.__init__
        def _patched_init(self, *args, **kwargs):
            if "generator" in kwargs:
                cg = _coerce_generator(kwargs["generator"])
                if cg is None:
                    kwargs.pop("generator")
                else:
                    kwargs["generator"] = cg
            return _ORIG_DATALOADER_INIT(self, *args, **kwargs)
        DataLoader.__init__ = _patched_init
    if _ORIG_MODULE_CALL is None:
        _ORIG_MODULE_CALL = nn.Module.__call__
        def _patched_call(self, *args, **kwargs):
            if not hasattr(self, "_global_device_bound"):
                try:
                    self.to(_DEVICE)
                except Exception:
                    pass
                self._global_device_bound = True
            args = _move(args)
            kwargs = _move(kwargs)

            try:
                if isinstance(self, nn.CrossEntropyLoss):
                    if len(args) >= 2 and torch.is_tensor(args[1]):
                        t = args[1]
                        if t.dtype != torch.long:
                            t = t.long()
                        if t.device != _DEVICE:
                            t = t.to(_DEVICE)
                        args = (args[0], t) + args[2:]
            except Exception:
                pass

            return _ORIG_MODULE_CALL(self, *args, **kwargs)
        nn.Module.__call__ = _patched_call

    if _ORIG_RANDOM_SPLIT is None:
        _ORIG_RANDOM_SPLIT = torch.utils.data.random_split
        def _patched_random_split(dataset, lengths, generator=None):
            g = _coerce_generator(generator)
            return _ORIG_RANDOM_SPLIT(dataset, lengths, generator=g)
        torch.utils.data.random_split = _patched_random_split

    if _ORIG_RANDPERM is None:
        _ORIG_RANDPERM = torch.randperm
        torch.randperm = _wrap_random(_ORIG_RANDPERM)
    if _ORIG_RAND is None:
        _ORIG_RAND = torch.rand
        torch.rand = _wrap_random(_ORIG_RAND)
    if _ORIG_RANDN is None:
        _ORIG_RANDN = torch.randn
        torch.randn = _wrap_random(_ORIG_RANDN)
    if _ORIG_RANDINT is None:
        _ORIG_RANDINT = torch.randint
        torch.randint = _wrap_random(_ORIG_RANDINT)
    if _ORIG_MULTINOMIAL is None:
        _ORIG_MULTINOMIAL = torch.multinomial
        torch.multinomial = _wrap_random(_ORIG_MULTINOMIAL)

# 임포트 시 자동 적용
_patch()