class Model:
    def as_dict(self):
        return self.__dict__

    def __repr__(self) -> str:
        return '<{name} {attributes} />'.format(
            name=self.__class__.__name__,
            attributes=' '.join('{}="{}"'.format(k, v) for k, v in self.__dict__.items())
        )
