from abc import ABC, abstractmethod

class AbstractDataLoader(ABC):
    @abstractmethod
    def load_data(self):
        pass
    @abstractmethod
    def clean_data(self, data):
        pass