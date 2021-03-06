import rdflib
import StringIO
import os
from contextlib import contextmanager
from caps.services import storage, identity
from caps.pilot.models import RDFMask


class Annotation(object):
    """
    what is an annotation?

    agent A asserts statement S about object O at datetime D
      where statement S has a property P and value V
      and value V possibly has type T and language L

    """
    # an annotation for now is a tuple of length 3 like follows:
    #   (subject, property, value) where:
    #   * subject is ark:/42409/foobarid
    #   * property is (dc, http://purl.org/dc/terms/, title)
    #     i.e., (label, vocab uri, element)
    #   * value is "Hamlet"
    pass


def add(identifier, annotation):
    # parse id (allow annotations of an ARK or part of an ARK)
    #   push this off till next phase and require all assertions
    #   to be at the object rather than file level
    pass

    # make sure id exists
    if not identity.exists(identifier):
        return False

    annotations = storage.get_or_create_file(identifier, "about.nt")
    # get_or_create annotations file from storage
    #   hardcode this filename to about.ttl?
# block out b.c. RDF lib was to sloooow
#    #annotations = storage.get_or_create_file(identifier, "about.n3")
#
#    # instantiate a graph
#    g = rdflib.ConjunctiveGraph()
#
#    if annotations:
#        # pull existing annotations into in-memory rdf graph
#        g.parse(StringIO.StringIO(annotations), format="n3")
#
#    # assume client sends list of strings/tuples (KLUDGE)
#    for assertion in annotation:
#        ns = rdflib.Namespace(assertion[1][1])
#        ns_label = assertion[1][0]
#        triple = (rdflib.URIRef(assertion[0]),
#                  ns[assertion[1][2]],
#                  rdflib.Literal(assertion[2]))
#
#        # attach annotation to annotations file
#        g.bind(ns_label, ns)
#        g.add(triple)
#
#        # write annotation to central datastore
#        #   push this off till future iteration
#        __rdfstore_write(triple, ns_label, ns)
# temp filx until we get rdf store working better
    if not annotations: 
        annotations = ""
    for assertion in annotation:
        trip = '<%s> <%s> "%s" .\n' % (assertion[0], assertion[1], assertion[2])
        RDFMask().create_mask(assertion[0], os.path.basename(assertion[1]), assertion[2])
        annotations += trip

    # validate annotations (don't write garbage)
    #   maybe rdflib is doing this for us in g.parse & g.add?
    pass

    # write annotations file using storage service
    #   this should ask storage to up the repo version
    # storage.put_file(identifier, "about.n3", g.serialize(format="n3"))
    storage.put_file(identifier, "about.nt", annotations) 

    return True

def query(q):
    """
    q should be a SPARQL query such as:

    SELECT ?title
    WHERE { ?subj <http://purl.org/dc/elements/1.1/title> ?title }

    which grabs all titles from any subject containing the dc:title pred.

    returns a list of hits
    """
    rdflib.plugin.register(
        'sparql', rdflib.query.Processor,
        'rdfextras.sparql.processor', 'Processor')
    rdflib.plugin.register(
        'sparql', rdflib.query.Result,
        'rdfextras.sparql.query', 'SPARQLQueryResult')
    with open_rdfstore() as graph:
        query_resp = graph.query(q)
    return query_resp.result

@contextmanager
def open_rdfstore(configString="/var/data/rdfstore.bdb", identifier=""):
    store = rdflib.plugin.get('Sleepycat', rdflib.store.Store)('rdfstore')
    graph = rdflib.ConjunctiveGraph(store='Sleepycat',
                                    identifier=identifier)
    try:
        rt = graph.open(configString, create=False)
        assert rt != rdflib.store.NO_STORE, "RDFstore is empty"
        assert rt == rdflib.store.VALID_STORE
        yield graph
    finally:
        graph.close()

def __rdfstore_write(triple, ns_label, ns):
    with open_rdfstore() as graph:
        graph.bind(ns_label, ns)
        graph.add(triple)
        graph.commit()
    return

def __dump_all():
    with open_rdfstore() as graph:
        n3 =  graph.serialize(format="n3")
    return n3

