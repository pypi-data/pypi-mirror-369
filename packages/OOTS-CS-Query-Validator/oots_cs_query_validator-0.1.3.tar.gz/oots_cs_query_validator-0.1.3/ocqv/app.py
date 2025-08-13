"""
Simple WSGI application for hosting the query evaluator. Will run an HTTP
server for development purposes if ran directly.
"""

import re
from argparse import ArgumentParser
from xml.etree.ElementTree import tostring

from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from .tools import QueryScheme, QueryReport
from .tools.parameter_evaluators import defined, url, code_list, specification

PATH_API_SEARCH = r"^/(\d+\.\d+\.\d+)/rest/search$"

PROCEDURE_ID = code_list(
    "Procedures-CodeList.gc",
    r"^[A-Z]+[1-9][0-9]*$")
COUNTRY_CODE = code_list(
    "EEA_Country-CodeList.gc",
    r"^[A-Z]{2}$")
NUTS_CODE = code_list(
    "NUTS2024-CodeList.gc",
    r"^[A-Z][A-Z]+[0-9]+$")
LAU_CODE = code_list(
    "LAU2022-CodeList.gc",
    r"^[A-Z]*[0-9]+$")

QUERY_SCHEMAS = {
    "urn:fdc:oots:eb:ebxml-regrep:queries:requirements-by-procedure-and-jurisdiction": {
        "1.2.0": QueryScheme({
            "queryId": defined
        }, {
            "procedure-id": PROCEDURE_ID,
            "country-code": COUNTRY_CODE,
            "jurisdiction-admin-l2": NUTS_CODE,
            "jurisdiction-admin-l3": LAU_CODE
        })
    },
    "urn:fdc:oots:eb:ebxml-regrep:queries:evidence-types-by-requirement-and-jurisdiction": {
        "1.2.0": QueryScheme({
            "queryId": defined
        }, {
            "requirement-id": url,
            "country-code": COUNTRY_CODE
        })
    },
    "urn:fdc:oots:dsd:ebxml-regrep:queries:dataservices-by-evidencetype-and-jurisdiction": {
        "1.2.0": QueryScheme({
            "queryId": defined,
            "evidence-type-classification": url,
            "country-code": COUNTRY_CODE
        }, {
            "jurisdiction-admin-l2": NUTS_CODE,
            "jurisdiction-admin-l3": LAU_CODE,
            "jurisdiction-context-id": defined,
            "EvidenceProviderClassification": defined,
            "specification": specification
        })
    }
}


@Request.application
def application(request: Request) -> Response:
    """
    Provides the WSGI application for the query evaluator.

    :param request: The request to handle.
    :return: An HTTP response.
    """
    match = re.fullmatch(PATH_API_SEARCH, request.path)

    if not match:
        raise NotFound()

    if "queryId" not in request.args:
        raise BadRequest()

    query_id = str(request.args.get("queryId"))

    if query_id not in QUERY_SCHEMAS:
        raise BadRequest()

    api_version = match.group(1)

    if api_version not in QUERY_SCHEMAS[query_id]:
        raise NotFound()  # a bit weird that a 404 can be thrown AFTER a 400

    if request.method not in ("GET", "HEAD"):
        raise MethodNotAllowed(valid_methods=("GET", "HEAD"))

    report = QueryReport({**request.args},
                         QUERY_SCHEMAS[query_id][api_version],
                         api_version).as_xml()

    return Response(
        tostring(report, encoding="utf-8", xml_declaration=True),
        content_type="application/xml; charset=utf-8"
    )


def cli():
    """
    Run the validator in a simple HTTP server, for debugging and development
    purposes.
    """
    parser = ArgumentParser(prog="ocqv",
                            description="Run the OOTS Common Services Query "
                                        "Validator development server.")

    parser.add_argument("-H", "--host", default="localhost",
                        help="hostname or IP address to bind to (default: "
                             "%(default)s)")
    parser.add_argument("-p", "--port", type=int, default=5000,
                        help="port to listen on (default: %(default)s)")
    parser.add_argument("-r", "--no-reload", action="store_true",
                        help="disable auto-reloader")
    parser.add_argument("-d", "--no-debug", action="store_true",
                        help="disable interactive debugger")
    parser.add_argument("-t", "--threaded", action="store_true",
                        help="enable multithreading")

    args = parser.parse_args()

    run_simple(args.host,
               args.port,
               application,
               use_reloader=not args.no_reload,
               use_debugger=not args.no_debug,
               threaded=args.threaded)


if __name__ == "__main__":
    cli()
