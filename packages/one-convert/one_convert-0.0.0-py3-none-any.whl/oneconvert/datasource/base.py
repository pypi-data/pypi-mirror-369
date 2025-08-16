import abc


@abc.abstractmethod
class BaseDataSource(object):
    @abc.abstractmethod
    def read(self): ...

    @abc.abstractmethod
    def write(self): ...
