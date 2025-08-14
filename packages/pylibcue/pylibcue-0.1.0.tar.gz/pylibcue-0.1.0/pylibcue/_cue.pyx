# cython: language_level=3

from libc.stdio cimport fdopen, fclose, FILE
from posix.unistd cimport dup
from pathlib import Path

from .cimport _libcue as libcue
from .mode import DiscMode, TrackMode, TrackSubMode

cdef dict _PTI = {
    "title": libcue.PTI_TITLE, "performer": libcue.PTI_PERFORMER,
    "songwriter": libcue.PTI_SONGWRITER, "composer": libcue.PTI_COMPOSER,
    "arranger": libcue.PTI_ARRANGER, "message": libcue.PTI_MESSAGE,
    "disc_id": libcue.PTI_DISC_ID, "genre": libcue.PTI_GENRE,
    "upc_isrc": libcue.PTI_UPC_ISRC, "size_info": libcue.PTI_SIZE_INFO,
    "toc_info": libcue.PTI_TOC_INFO1
}

cdef dict _REM = {
    "date": libcue.REM_DATE,
    "alnum_gain": libcue.REM_REPLAYGAIN_ALBUM_GAIN,
    "album_peak": libcue.REM_REPLAYGAIN_ALBUM_PEAK,
    "track_gain": libcue.REM_REPLAYGAIN_TRACK_GAIN,
    "track_peak": libcue.REM_REPLAYGAIN_TRACK_PEAK,
}

cdef class CDText:
    cdef:
        libcue.Cdtext *_cdtext
        Cd _ref

        void _init(self, libcue.Cdtext *cdtext, Cd ref):
            if cdtext is NULL:
                raise MemoryError
            self._cdtext = cdtext
            self._ref = ref

    def __init__(self):
        raise NotImplementedError

    def __getattr__(self, item):
        cdef const char *content = libcue.cdtext_get(_PTI[item], self._cdtext)
        if content is NULL:
            return None
        return content.decode(encoding=self._ref.encoding)

cdef class Rem:
    cdef:
        libcue.Rem *_rem
        Cd _ref

        void _init(self, libcue.Rem *rem, Cd ref):
            if rem is NULL:
                raise MemoryError
            self._rem = rem
            self._ref = ref

    def __init__(self):
        raise NotImplementedError

    def __getattr__(self, item):
        cdef const char *content = libcue.rem_get(_REM[item], self._rem)
        if content is NULL:
            return None
        return content.decode(encoding=self._ref.encoding)

cdef class Cd:
    cdef:
        libcue.Cd *_cd
        readonly str encoding

        void _init(self, libcue.Cd *cd, str encoding):
            if cd is NULL:
                raise MemoryError
            self._cd = cd
            self.encoding = encoding

    def __dealloc__(self):
        if self._cd is not NULL:
            libcue.cd_delete(self._cd)
            self._cd = NULL

    cdef int get_ntrack(self) nogil:
        return libcue.cd_get_ntrack(self._cd)

    # public

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Use classmethods (.from_str .from_file etc.) to create Cd object from cue."
        )

    @classmethod
    def from_file(cls, object file, str encoding="utf-8"):
        cdef FILE *f = fdopen(dup(file.fileno()), b'r')
        if f is NULL:
            raise IOError("Failed to read file.")

        cdef libcue.Cd *cd = libcue.cue_parse_file(f)
        fclose(f)
        if cd is NULL:
            raise ValueError("Failed to parse cue file.")

        cdef Cd obj = cls.__new__(cls)
        obj._init(cd, encoding)
        return obj

    @classmethod
    def from_str(cls, str string):
        encoded = string.encode()
        cdef const char *content = encoded
        cdef libcue.Cd *cd = libcue.cue_parse_string(content)
        if cd is NULL:
            raise ValueError("Failed to parse cue string.")
        cdef Cd obj = cls.__new__(cls)
        obj._init(cd, "utf-8")
        return obj

    @classmethod
    def from_path(cls, object path, str encoding="utf-8"):
        _path = Path(path)
        with _path.open("r", encoding=encoding) as f:
            return cls.from_file(f, encoding)

    @property
    def cdtext(self):
        cdef CDText cdtext = CDText.__new__(CDText)
        cdtext._init(libcue.cd_get_cdtext(self._cd), self)
        return cdtext

    @property
    def rem(self):
        cdef Rem rem = Rem.__new__(Rem)
        rem._init(libcue.cd_get_rem(self._cd), self)
        return rem

    @property
    def cdtextfile(self):
        cdef const char *content = libcue.cd_get_cdtextfile(self._cd)
        if content is NULL:
            return None
        return content.decode(encoding=self.encoding)

    @property
    def mode(self):
        return DiscMode(<int> libcue.cd_get_mode(self._cd))

    def __len__(self):
        return self.get_ntrack()

    def __getitem__(self, int index):
        if index < 0 or index >= self.get_ntrack():
            raise IndexError("Track index out of range")
        cdef Track track = Track.__new__(Track)
        track._init(libcue.cd_get_track(self._cd, index + 1), self)
        return track

cdef class Track:
    cdef:
        libcue.Track *_track
        Cd _ref

        void _init(self, libcue.Track *track, Cd ref):
            if track is NULL:
                raise MemoryError
            self._track = track
            self._ref = ref

    # public

    def __init__(self):
        raise NotImplementedError

    @property
    def cdtext(self):
        cdef CDText cdtext = CDText.__new__(CDText)
        cdtext._init(libcue.track_get_cdtext(self._track), self._ref)
        return cdtext

    @property
    def rem(self):
        cdef Rem rem = Rem.__new__(Rem)
        rem._init(libcue.track_get_rem(self._track), self._ref)
        return rem

    @property
    def filename(self):
        cdef const char *filename = libcue.track_get_filename(self._track)
        if filename is NULL:
            return None
        return filename.decode(encoding=self._ref.encoding)

    @property
    def start(self):
        cdef long start = libcue.track_get_start(self._track)
        return f2msf(start) if start > 0 else None

    @property
    def length(self):
        cdef long length = libcue.track_get_length(self._track)
        return f2msf(length) if length > 0 else None

    @property
    def zero_pre(self):
        cdef long length = libcue.track_get_zero_pre(self._track)
        return f2msf(length) if length > 0 else None

    @property
    def zero_post(self):
        cdef long length = libcue.track_get_zero_post(self._track)
        return f2msf(length) if length > 0 else None

    @property
    def isrc(self):
        cdef const char *content = libcue.track_get_isrc(self._track)
        if content is NULL:
            return None
        return content.decode(encoding=self._ref.encoding)

    @property
    def mode(self):
        return TrackMode(<int> libcue.track_get_mode(self._track))

    @property
    def submode(self):
        return TrackSubMode(<int> libcue.track_get_sub_mode(self._track))

    cpdef has_flag(self, int flag):
        cdef bint ret = libcue.track_is_set_flag(self._track, <libcue.TrackFlag> flag)
        return ret

    def __and__(self, int other):
        return self.has_flag(other)

cdef tuple f2msf(const long frames):
    cdef long seconds = frames // 75
    cdef long minutes = seconds // 60
    return minutes, seconds % 60, frames % 75
