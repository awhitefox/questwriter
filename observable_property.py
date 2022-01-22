class ObservableProperty:
    def __init__(self, signal_name: str):
        self.attr_name = ''
        self.signal_name = signal_name

    def __set_name__(self, owner, name):
        self.attr_name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.attr_name)

    def __set__(self, instance, value):
        setattr(instance, self.attr_name, value)
        getattr(instance, self.signal_name).emit(value)
