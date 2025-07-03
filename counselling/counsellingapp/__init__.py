def ready(self):
    import counsellingapp.signals  # or wherever your signals.py is located
    return counsellingapp.signals.ready()  # or whatever your signal function is named