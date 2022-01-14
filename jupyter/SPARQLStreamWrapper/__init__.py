# -*- coding: utf8 -*-

"""

**SPARQLStreamWrapper** is a simple Python wrapper around a `SPARQL <https://www.w3.org/TR/sparql11-overview/>`_ service to
remotelly execute your queries in a streaming format. It helps in creating the query
invokation and, possibly, convert the result into a more manageable format.

"""

__version__ = "0.1.dev0"
"""The version of SPARQLStreamWrapper, a streaming extension under development of SPARQLWrapper"""

__authors__ = "Matteo Belcao"
"""The primary authors of SPARQLStreamWrapper"""

__license__ = "W3C® SOFTWARE NOTICE AND LICENSE, http://www.w3.org/Consortium/Legal/copyright-software"
"""The license governing the use and distribution of SPARQLWrapper"""

__url__ = "https://github.com/chimera-suite"
"""The URL for Chimera Suite"""

__contact__ = "matteo.belcao@mail.polimi.it,matteo.belcao@quantiaconsulting.com"
"""Some mails of the developer involved in the project"""

__date__ = "2022-01-02"
"""Last update"""

__agent__ = "sparqlstreamwrapper %s (https://github.com/chimera-suite)" % __version__


from .Wrapper import SPARQLStreamWrapper
from .Wrapper import XML, JSON, JSONL, TURTLE, N3, JSONLD, RDF, RDFXML, CSV, TSV
from .Wrapper import GET, POST
from .Wrapper import SELECT, CONSTRUCT, ASK, DESCRIBE, INSERT, DELETE
from .Wrapper import URLENCODED, POSTDIRECTLY
from .Wrapper import BASIC, DIGEST
