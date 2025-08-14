import shapely
import matplotlib.collections
from matplotlib.path import Path

import esy.osm.shape


def render(shapes, path_patch_options, point_radius=0.0001):
    pathpatches = []
    for shape, path_patch_option in zip(shapes, path_patch_options):
        if type(shape) is shapely.geometry.LineString:
            pathpatches.append(matplotlib.patches.PathPatch(
                matplotlib.path.Path(list(shape.coords), closed=False),
                **{'fill': False, **path_patch_option},
            ))
        elif type(shape) is shapely.geometry.LinearRing:
            pathpatches.append(matplotlib.patches.PathPatch(
                matplotlib.path.Path(list(shape.coords), closed=True),
                **{'fill': False, **path_patch_option},
            ))
        elif type(shape) is shapely.geometry.Polygon:
            vertices = list(shape.exterior.coords)
            codes = (
                [Path.MOVETO] +
                [Path.LINETO] * (len(vertices) - 2) +
                [Path.CLOSEPOLY]
            )

            for ring in shape.interiors:
                ring_vertices = list(ring.coords)
                ring_codes = (
                    [Path.MOVETO] +
                    [Path.LINETO] * (len(ring_vertices) - 2) +
                    [Path.CLOSEPOLY]
                )
                vertices += ring_vertices
                codes += ring_codes
            pathpatches.append(matplotlib.patches.PathPatch(
                matplotlib.path.Path(vertices, codes, closed=True),
                **{'fill': True, **path_patch_option},
            ))
        elif type(shape) is shapely.geometry.MultiPolygon:
            for shape in shape.geoms:
                vertices = list(shape.exterior.coords)
                codes = (
                    [Path.MOVETO] +
                    [Path.LINETO] * (len(vertices) - 2) +
                    [Path.CLOSEPOLY]
                )

                for ring in shape.interiors:
                    ring_vertices = list(ring.coords)
                    ring_codes = (
                        [Path.MOVETO] +
                        [Path.LINETO] * (len(ring_vertices) - 2) +
                        [Path.CLOSEPOLY]
                    )
                    vertices += ring_vertices
                    codes += ring_codes
                pathpatches.append(matplotlib.patches.PathPatch(
                    matplotlib.path.Path(vertices, codes, closed=True),
                    **{'fill': True, **path_patch_option},
                ))
        elif type(shape) is shapely.geometry.Point:
            pathpatches.append(matplotlib.patches.PathPatch(
                matplotlib.path.Path.circle(
                    center=(shape.x, shape.y), radius=point_radius
                ),
                **{'edgecolor': 'none', **path_patch_option},
            ))
        else:
            raise ValueError('Unsupported shape type {}'.format(shape))

    return pathpatches


def patches(shapes, path_patch_options):
    return matplotlib.collections.PatchCollection(
        render(shapes, path_patch_options), match_original=True
    )


simple_style = {
    'landuse': {
        'forest': {'color': 'forestgreen'},
        'industrial': {'color': 'slateblue'},
        'commercial': {'color': 'mediumpurple'},
        'grass': {'color': 'yellowgreen'},
        'meadow': {'color': 'yellowgreen'},
        'greenfield': {'color': 'yellowgreen'},
        'farmland': {'color': 'wheat'},
        'residential': {'color': 'lightgray'},
    },
    'natural': {
        'bare_rock': {'color': 'darkgray'},
        'rock': {'color': 'darkgray'},
        'forest': {'color': 'forestgreen'},
        'wood': {'color': 'forestgreen'},
        'grass': {'color': 'yellowgreen'},
        'grassland': {'color': 'yellowgreen'},
        'wetland': {'color': 'olivedrab'},
        'cliff': {'color': 'purple'},
        'water': {'color': 'deepskyblue'},
    },
    'water': {
        'river': {'color': 'deepskyblue'},
        'pond': {'color': 'deepskyblue'},
        'lake': {'color': 'deepskyblue'},
        'lagoon': {'color': 'deepskyblue'},
    },
    'waterway': {
        'river': {'color': 'deepskyblue'},
        'stream': {'color': 'deepskyblue'},
        'canal': {'color': 'deepskyblue'},
    },
    'boundary': {
        'administrative': {'edgecolor': 'dimgray', 'linestyle': '--', 'facecolor': 'none'},
        'national_park': {'color': 'tan'},
    },
    'highway': {
        'primary': {'color': 'darkgray', 'linewidth': 2, 'fill': False},
        'secondary': {'color': 'darkgray', 'fill': False},
        'path': {'color': 'darkgray', 'linestyle': 'dotted', 'fill': False},
    },
    'building': {
        'yes': {'edgecolor': 'dimgrey', 'facecolor': 'darkgray'},
        'house': {'edgecolor': 'dimgrey', 'facecolor': 'darkgray'},
        'residential': {'edgecolor': 'dimgrey', 'facecolor': 'darkgray'},
        'commercial': {'edgecolor': 'slateblue', 'facecolor': 'mediumpurple'},
        'industrial': {'edgecolor': 'navy', 'facecolor': 'slateblue'},
    },
}


def filter(style):
    tagset = set(style)
    return lambda entry: not tagset.isdisjoint(entry.tags)


def render_map(style, items):
    return matplotlib.collections.PatchCollection(
        render(*zip(*(
            (shape, tag_style[tags[name]])
            for name, tag_style in style.items()
            for shape, _, tags in items
            if type(shape) is not esy.osm.shape.Invalid
            if tags.get(name) in tag_style
        ))), match_original=True
    )
