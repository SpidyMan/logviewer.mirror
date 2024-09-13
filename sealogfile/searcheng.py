"""
Editra Business Model Library: SearchEngine

Text Search Engine for finding text and grepping files
"""

__author__ = "Cody Precord <cprecord@editra.org>"

__all__ = ['SearchEngine', ]

#-----------------------------------------------------------------------------#
# Imports
import os
import re
import fnmatch
from io import StringIO

class FileTypeChecker(object):
    """File type checker and recognizer"""
    TXTCHARS = bytes([7, 8, 9, 10, 12, 13, 27] + list(range(0x20, 0x7F)))
    ALLBYTES = bytes(range(256))

    def __init__(self, preread=4096):
        """Create the FileTypeChecker
        @keyword preread: number of bytes to read for checking file type
        """
        self._preread = preread

    @staticmethod
    def _GetHandle(fname):
        """Get a file handle for reading
        @param fname: filename
        @return: file object or None
        """
        try:
            handle = open(fname, 'rb')
        except IOError:
            handle = None
        return handle

    def IsBinary(self, fname):
        """Check if the file contains binary data."""
        handle = self._GetHandle(fname)
        if handle is not None:
            bytes_content = handle.read(self._preread)
            handle.close()
            # Translate: Delete all text characters (keep only binary ones)
            nontext = bytes_content.translate(None, FileTypeChecker.TXTCHARS)
            return bool(nontext)  # If any non-text characters exist, it's binary
        else:
            return False

    def IsReadableText(self, fname):
        """Check if the given path is readable as text."""
        f_ok = False
        if os.access(fname, os.R_OK):
            f_ok = not self.IsBinary(fname)
        return f_ok

#-----------------------------------------------------------------------------#

class SearchEngine(object):
    """Text Search Engine
    All Search* methods are iterable generators.
    All Find* methods do a complete search and return the match collection.
    """
    def __init__(self, query, regex=True, down=True,
                 matchcase=True, wholeword=False):
        """Initialize a search engine object
        @param query: search string
        @keyword regex: Is a regex search
        @keyword down: Search down or up
        @keyword matchcase: Match case
        @keyword wholeword: Match whole word
        """
        # Attributes
        self._isregex = regex
        self._next = down
        self._matchcase = matchcase
        self._wholeword = wholeword
        self._unicode = False
        self._query = query
        self._regex = ''
        self._pool = ''
        self._lmatch = None             # Last match object
        self._filters = None            # File Filters
        self._formatter = lambda f, l, m: "%s %d: %s" % (f, l+1, m)
        self._CompileRegex()

    def _CompileRegex(self):
        """Prepare and compile the regex object based on the current state and settings."""
        tmp = self._query
        if not self._isregex:
            tmp = re.escape(tmp)

        if self._wholeword:
            tmp = r"\b%s\b" % tmp

        flags = re.MULTILINE

        if not self._matchcase:
            flags |= re.IGNORECASE

        if self._unicode:
            flags |= re.UNICODE

        try:
            self._regex = re.compile(tmp, flags)
        except re.error:
            self._regex = None

    def ClearPool(self):
        """Clear the search pool"""
        self._pool = ""

    def Find(self, spos=0):
        """Find the next match based on the state of the search engine."""
        if self._regex is None:
            return None

        if self._next:
            return self.FindNext(spos)
        else:
            if spos == 0:
                spos = -1
            return self.FindPrev(spos)

    def FindAll(self):
        """Find all the matches in the current context."""
        if self._regex is None:
            return []

        matches = [match for match in self._regex.finditer(self._pool)]
        return matches

    def FindAllLines(self, stc=None):
        """Find all the matches in the current context and return the lines."""
        rlist = []
        if self._regex is None:
            return rlist

        if stc:
            linecount = stc.GetLineCount()
            for lnum in range(linecount):
                line = stc.GetLineRaw(lnum)
                match = self._regex.search(line)
                if match is not None:
                    rlist.append((self._formatter("Line", lnum, line), (lnum+1, match.span())))
        else:
            for lnum, line in enumerate(StringIO(self._pool)):
                match = self._regex.search(line)
                if match is not None:
                    rlist.append((self._formatter("Line", lnum, line), (lnum+1, match.span())))

        return rlist

    def FindNext(self, spos=0):
        """Find the next match of the query starting at spos."""
        if self._regex is None:
            return None

        if spos < len(self._pool):
            match = self._regex.search(self._pool[spos:])
            if match is not None:
                self._lmatch = match
                return match.span()
        return None

    def FindPrev(self, spos=-1):
        """Find the previous match of the query starting at spos."""
        if self._regex is None:
            return None

        if spos+1 < len(self._pool):
            matches = [match for match in self._regex.finditer(self._pool[:spos])]
            if len(matches):
                lmatch = matches[-1]
                self._lmatch = lmatch
                return (lmatch.start(), lmatch.end())
        return None

    def GetLastMatch(self):
        """Get the last found match object."""
        return self._lmatch

    def GetOptionsString(self):
        """Get a string describing the search engine's options."""
        rstring = "\"%s\" [ " % self._query
        for desc, attr in (("regex: %s", self._isregex),
                           ("match case: %s", self._matchcase),
                           ("whole word: %s", self._wholeword)):
            rstring += (desc % "on; " if attr else desc % "off; ")
        rstring += "]"
        return rstring

    def GetQuery(self):
        """Get the raw query string."""
        return self._query

    def GetQueryObject(self):
        """Get the regex object used for the search."""
        return self._regex

    def GetSearchPool(self):
        """Get the search pool string."""
        return self._pool

    def IsMatchCase(self):
        """Check if case-sensitive search is enabled."""
        return self._matchcase

    def IsRegEx(self):
        """Check if regex search is enabled."""
        return self._isregex

    def IsWholeWord(self):
        """Check if whole word matching is enabled."""
        return self._wholeword

    def SearchInDirectory(self, directory, recursive=True):
        """Search in all files within a directory."""
        if self._regex is None:
            return

        # Get all files in the directory
        paths = [os.path.join(directory, fname)
                 for fname in os.listdir(directory) if not fname.startswith('.')]

        # Filter files based on filters
        if self._filters:
            paths = [fname for fname in paths if any(fnmatch.fnmatch(fname, pat) for pat in self._filters)]

        # Search in the paths
        for path in paths:
            if recursive and os.path.isdir(path):
                for match in self.SearchInDirectory(path, recursive):
                    yield match
            else:
                for match in self.SearchInFile(path):
                    yield match
        return

    def SearchInFile(self, fname):
        """Search in a file for all lines with matches of the set query."""
        if self._regex is None:
            return

        checker = FileTypeChecker()
        if checker.IsReadableText(fname):
            try:
                fobj = open(fname, 'r')
            except (IOError, OSError):
                return
            else:
                yield (None, fname)  # Special token to signify start of a search

            start = 0
            for lnum, line in enumerate(fobj):
                match = self._regex.search(line)
                if match is not None:
                    span = match.span()
                    yield self._formatter(fname, lnum, line, (span[0] + start, span[1] + start))
                start += len(line) + 1
            fobj.close()
        return

    def SearchInFiles(self, flist):
        """Search in a list of files."""
        if self._regex is None:
            return

        for fname in flist:
            for match in self.SearchInFile(fname):
                yield match
        return

    def SetFileFilters(self, filters):
        """Set file filters to specify the type of files to search."""
        self._filters = filters

    def SetFormatter(self, formatter):
        """Set the formatter used to create match lines."""
        self._formatter = formatter

    def SetSearchPool(self, pool):
        """Set the search pool used by the Find methods."""
        self._pool = pool
        if isinstance(self._pool, str):  # Use 'str' for Python 3
            self._unicode = True
            self._CompileRegex()


# Create a search engine object
search_engine = SearchEngine(query="def", regex=False, matchcase=False)

# Set file filters to only search Python files
search_engine.SetFileFilters(['*.py'])

# Search within a directory (non-recursive in this case)
for match in search_engine.SearchInDirectory('.', recursive=False):
    print(match)