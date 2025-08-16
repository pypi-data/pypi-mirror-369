import luigi

class IndexedLocalTarget(luigi.LocalTarget):
    class _IndexFormat:
        def __init__(self, ext):
            self.ext = ext

    TBI = _IndexFormat('tbi')
    CSI = _IndexFormat('csi')

    def __init__(self, path, index_format=TBI):
        """
        :param: format: an extension for the indexed format, which defaults to tbi
        """
        super(IndexedLocalTarget, self).__init__(path)
        self._index_target = luigi.LocalTarget(path + '.' + index_format.ext)

    def remove(self, *args, **kwds):
        super(IndexedLocalTarget, self).remove(*args, **kwds)
        self._index_target.remove(*args, **kwds)

    def exists(self):
        return super(IndexedLocalTarget, self).exists() and self._index_target.exists()
