from viking.core import Plugin

class Enumerator(Plugin):
    def __iter__(self):
        raise NotImplementedError


class FileEnumerator(Enumerator):
    def __iter__(self):
        with open(self.uri.path, 'rb') as fd:
            for line in fd:
                line = line.strip()

                if not line: continue

                if line.startswith('#'): continue

                for item in line.split():
                    yield item
