
import time
class Timer:
    def __init__(self, name="", store=None):
        self.name=name; self.store=store; self.dt_ms=0.0
    def __enter__(self):
        self.t0=time.perf_counter(); return self
    def __exit__(self, exc_type, exc, tb):
        self.dt_ms=(time.perf_counter()-self.t0)*1000.0
        if self.store is not None and self.name:
            self.store[self.name]=self.store.get(self.name,0.0)+self.dt_ms
class Counter:
    def __init__(self): self.counts={}
    def inc(self, key, by=1): self.counts[key]=self.counts.get(key,0)+by
    def get(self, key): return self.counts.get(key,0)
