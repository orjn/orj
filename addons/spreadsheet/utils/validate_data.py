from collections import defaultdict
from itertools import chain
import json
import re

markdown_link_regex = r"^\[([^\[]+)\]\((.+)\)$"

xml_id_url_prefix = "orj://ir_menu_xml_id/"

orj_view_link_prefix = "orj://view/"


def orj_charts(data):
    """return all orj chart definition in the spreadsheet"""
    figures = []
    for sheet in data.get("sheets", []):
        figures += [
            dict(figure["data"], id=figure["id"])
            for figure in sheet.get("figures", [])
            if figure["tag"] == "chart" and figure["data"]["type"].startswith("orj_")
        ]
    return figures


def links_urls(data):
    """return all markdown links in cells"""
    urls = []
    link_prefix = "orj://view/"
    for sheet in data.get("sheets", []):
        for cell in sheet.get("cells", {}).values():
            content = cell.get("content", "")
            match = re.match(markdown_link_regex, content)
            if match and match.group(2).startswith(link_prefix):
                urls.append(match.group(2))
    return urls


def orj_view_links(data):
    """return all view definitions embedded in link cells.
    urls looks like orj://view/{... view data...}
    """
    return [
        json.loads(url[len(orj_view_link_prefix):])
        for url in links_urls(data)
        if url.startswith(orj_view_link_prefix)
    ]


def remove_aggregator(field_name):
    """remove the group operator
    >>> remove_aggregator("amount:sum")
    >>> "amount"
    """
    return field_name.split(":")[0]


def domain_fields(domain):
    """return all field names used in the domain"""
    fields = []
    for leaf in domain:
        if len(leaf) == 3:
            fields.append(leaf[0])
    return fields


def pivot_measure_fields(pivot):
    measures = [
        measure if isinstance(measure, str)
        # "field" has been renamed to "name" and "name" to "fieldName"
        else measure["field"] if "field" in measure
        else measure["name"] if "name" in measure
        else measure["fieldName"]
        for measure in pivot["measures"]
        if "computedBy" not in measure
    ]
    return [
        measure
        for measure in measures
        if measure != "__count"
    ]


def pivot_fields(pivot):
    """return all field names used in a pivot definition"""
    model = pivot["model"]
    fields = set(
        # colGroupBys and rowGroupBys were renamed to columns and rows, name to fieldName
        pivot.get("colGroupBys", []) + [col.get("name", col.get("fieldName")) for col in pivot.get("columns", [])]
        + pivot.get("rowGroupBys", []) + [row.get("name", row.get("fieldName")) for row in pivot.get("rows", [])]
        + pivot_measure_fields(pivot)
        + domain_fields(pivot["domain"])
    )
    measure = pivot.get("sortedColumn") and pivot["sortedColumn"]["measure"]
    if measure and measure != "__count":
        fields.add(measure)
    return model, fields


def list_order_fields(list_definition):
    return [order["name"] for order in list_definition["orderBy"]]


def list_fields(list_definition):
    """return all field names used in a list definitions"""
    model = list_definition["model"]
    fields = set(
        list_definition["columns"]
        + list_order_fields(list_definition)
        + domain_fields(list_definition["domain"])
    )
    return model, fields


def chart_fields(chart):
    """return all field names used in a chart definitions"""
    model = chart["metaData"]["resModel"]
    fields = set(
        chart["metaData"]["groupBy"]
        + chart["searchParams"]["groupBy"]
        + domain_fields(chart["searchParams"]["domain"])
    )
    measure = chart["metaData"]["measure"]
    if measure != "__count":
        fields.add(measure)
    return model, fields


def filter_fields(data):
    """return all field names used in global filter definitions"""
    fields_by_model = defaultdict(set)
    charts = orj_charts(data)
    orj_version = data.get("orjVersion", 1)
    if orj_version < 5:
        for filter_definition in data.get("globalFilters", []):
            for pivot_id, matching in filter_definition.get("pivotFields", dict()).items():
                model = data["pivots"][pivot_id]["model"]
                fields_by_model[model].add(matching["field"])
            for list_id, matching in filter_definition.get("listFields", dict()).items():
                model = data["lists"][list_id]["model"]
                fields_by_model[model].add(matching["field"])
            for chart_id, matching in filter_definition.get("graphFields", dict()).items():
                chart = next((chart for chart in charts if chart["id"] == chart_id), None)
                model = chart["metaData"]["resModel"]
                fields_by_model[model].add(matching["field"])
    else:
        for pivot in data["pivots"].values():
            if pivot.get("type", "ORJ") == "ORJ":
                model = pivot["model"]
                field = pivot.get("fieldMatching", {}).get("chain")
                if field:
                    fields_by_model[model].add(field)
        for _list in data["lists"].values():
            model = _list["model"]
            field = _list.get("fieldMatching", {}).get("chain")
            if field:
                fields_by_model[model].add(field)
        for chart in charts:
            model = chart["metaData"]["resModel"]
            field = chart.get("fieldMatching", {}).get("chain")
            if field:
                fields_by_model[model].add(field)

    return dict(fields_by_model)


def orj_view_fields(view):
    return view["action"]["modelName"], set(domain_fields(view["action"]["domain"]))


def extract_fields(extract_fn, items):
    fields_by_model = defaultdict(set)
    for item in items:
        model, fields = extract_fn(item)
        fields_by_model[model] |= {remove_aggregator(field) for field in fields}
    return dict(fields_by_model)


def fields_in_spreadsheet(data):
    """return all fields, grouped by model, used in the spreadsheet"""
    orj_pivots = (pivot for pivot in data.get("pivots", dict()).values() if pivot.get("type", "ORJ") == "ORJ")
    all_fields = chain(
        extract_fields(list_fields, data.get("lists", dict()).values()).items(),
        extract_fields(pivot_fields, orj_pivots).items(),
        extract_fields(chart_fields, orj_charts(data)).items(),
        extract_fields(orj_view_fields, orj_view_links(data)).items(),
        filter_fields(data).items(),
    )
    fields_by_model = defaultdict(set)
    for model, fields in all_fields:
        fields_by_model[model] |= fields
    return dict(fields_by_model)


def menus_xml_ids_in_spreadsheet(data):

    return set(data.get("chartOrjMenusReferences", {}).values()) | {
        url[len(xml_id_url_prefix):]
        for url in links_urls(data)
        if url.startswith(xml_id_url_prefix)
    }
