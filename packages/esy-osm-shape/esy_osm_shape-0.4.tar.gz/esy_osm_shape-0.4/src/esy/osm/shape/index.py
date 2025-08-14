import sys, zlib, itertools, pickle
from bisect import bisect

import shapely.geometry

import esy.osm.pbf.index
from esy.osm.pbf.file import (
    decode_strmap, iter_nodes, iter_ways, iter_relations, Node, Way, Relation
)
from esy.osm.shape.shape import multipolygon_shape


_blob = esy.osm.pbf.fileformat_pb2.Blob()


def parse_header_block(file, block):
    if block.header.type != 'OSMHeader':
        raise ValueError(f'Blob type {block.header.type} is not "OSMHeader"')
    file.seek(block.ofs)
    osmheader = esy.osm.pbf.osmformat_pb2.HeaderBlock()
    osmheader.ParseFromString(esy.osm.pbf.file.read_blob(
        file, block.ofs, block.header.datasize
    ))
    return osmheader


def unsupported(osm, entry):
    description = '{} (id={})'.format(type(entry).__name__, entry.id)
    return (None, entry.id, {'@error': description})
    yield


def point(osm, node):
    shape = shapely.Point(node.lonlat)
    return (shape, node.id, node.tags)
    yield


def linestring(osm, way):
    shape = shapely.LineString(
        [n.lonlat for n in (yield esy.osm.pbf.Node, way.refs)]
    )
    return (shape, way.id, way.tags)


def polygon(osm, way):
    outer = shapely.LinearRing(
        [n.lonlat for n in (yield esy.osm.pbf.Node, way.refs)]
    )

    # Switch winding order if necessary.
    if not outer.is_ccw:
        outer = shapely.geometry.polygon.LinearRing(outer.coords[::-1])

    shape = shapely.geometry.Polygon(outer)
    return (shape if shape.is_valid else None, way.id, way.tags)


def multipolygon(osm, relation):
    way_ids = set(
        id for id, type, role in relation.members if type == 'WAY'
    )

    ways = {way.id: way for way in (yield esy.osm.pbf.Way, way_ids)}

    node_ids = set.union(*(set(w.refs) for w in ways.values()))
    nodes = {entry.id: entry for entry in (yield esy.osm.pbf.Node, node_ids)}

    shape = multipolygon_shape(relation, ways, nodes)
    return (shape if shape.is_valid else None, relation.id, relation.tags)


def shape_function(entry):
    entry_type = type(entry)
    if entry_type is esy.osm.pbf.Node:
        return point
    elif entry_type is esy.osm.pbf.Way:
        if entry.tags.get('area') != 'no' and entry.refs[0] == entry.refs[-1]:
            return polygon
        else:
            return linestring
    elif entry_type is esy.osm.pbf.Relation:
        if entry.tags.get('type') == 'multipolygon':
            return multipolygon
    return unsupported


osmtypeidxmap = {
    type: idx for idx, type in enumerate(
        (esy.osm.pbf.Node, esy.osm.pbf.Way, esy.osm.pbf.Relation)
    )
}


class Shape(object):
    def __init__(self, osm):
        if type(osm) is str:
            osm = esy.osm.pbf.index.Index(osm)
        self.osm = osm

        header = parse_header_block(self.osm.pbf.file, next(self.osm.pbf.blocks))
        self.box = shapely.geometry.box(
            header.bbox.left / 1000000000, header.bbox.bottom / 1000000000,
            header.bbox.right / 1000000000, header.bbox.top / 1000000000
        )

    def __call__(self, filter=None, max_tasks=2 ** 16):
        tasks = []
        for entry in self.osm:
            if filter is not None and not filter(entry):
                continue

            tasks.append(shape_function(entry)(self, entry))
            if len(tasks) < max_tasks:
                continue

            yield from self._process(tasks)
            del tasks[:]

        yield from self._process(tasks)

    def load(self, entries):
        return self._process([
            shape_function(entry)(self, entry) for entry in entries
        ])

    def _process(self, tasks):
        results, queries, requests = {}, (set(), set(), set()), []
        queue = [(generator, True, None) for generator in tasks]
        while queue:
            for generator, ok, value in queue:
                try:
                    if ok:
                        osmtype, ids = generator.send(value)
                    else:
                        osmtype, ids = generator.throw(value)
                except StopIteration as e:
                    results[generator] = e.args[0]
                    continue

                osmtypeidx = osmtypeidxmap[osmtype]
                queries[osmtypeidx].update(ids)
                requests.append((generator, osmtypeidx, ids))

            del queue[:]
            if not requests:
                continue

            # Query data.
            dataset = self.osm(queries)
            for generator, osmtypeidx, ids in requests:
                try:
                    map = dataset[osmtypeidx]
                    queue.append((generator, True, [map[id] for id in ids]))
                except KeyError as error:
                    import traceback
                    traceback.print_exc()
                    queue.append((generator, False, error))

            # Release memory.
            del dataset
            del requests[:]
            for query in queries:
                query.clear()

        for task in tasks:
            yield results[task]
