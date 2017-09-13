# -*- coding: utf8 -*-
"""In the Spotlight analysis module."""

import datetime
import itertools
import enki
from libcrowds_analyst.analysis import helpers
from libcrowds_analyst import object_loader


MERGE_RATIO = 0.5


def get_overlap_ratio(r1, r2):
    """Return the overlap ratio of two rectangles."""
    r1x2 = r1['x'] + r1['w']
    r2x2 = r2['x'] + r2['w']
    r1y2 = r1['y'] + r1['h']
    r2y2 = r2['y'] + r2['h']

    x_overlap = max(0, min(r1x2, r2x2) - max(r1['x'], r2['x']))
    y_overlap = max(0, min(r1y2, r2y2) - max(r1['y'], r2['y']))
    intersection = x_overlap * y_overlap

    r1_area = r1['w'] * r1['h']
    r2_area = r2['w'] * r2['h']
    union = r1_area + r2_area - intersection

    overlap = float(intersection) / float(union)
    print overlap
    return overlap


def get_rect_from_selection(anno):
    """Return a rectangle from a selection annotation."""
    media_frag = anno['target']['selector']['value']
    regions = media_frag.split('=')[1].split(',')
    return {
        'x': int(round(float(regions[0]))),
        'y': int(round(float(regions[1]))),
        'w': int(round(float(regions[2]))),
        'h': int(round(float(regions[3])))
    }


def merge_rects(r1, r2):
    """Merge two rectangles."""
    return {
        'x': min(r1['x'], r2['x']),
        'y': min(r1['y'], r2['y']),
        'w': max(r1['x'] + r1['w'], r2['x'] + r2['w']) - r2['x'],
        'h': max(r1['y'] + r1['h'], r2['y'] + r2['h']) - r2['y']
    }


def update_selector(anno, rect):
    """Update amedia frag selector."""
    frag = '?xywh={0},{1},{2},{3}'.format(rect['x'], rect['y'], rect['w'],
                                          rect['h'])
    anno['target']['selector']['value'] = frag
    anno['modified'] = datetime.datetime.now().isoformat()


def analyse_selections(api_key, endpoint, project_id, result_id, path, doi,
                       project_short_name, **kwargs):
    """Analyse In the Spotlight selection results."""
    e = enki.Enki(api_key, endpoint, project_short_name, all=1)
    result = enki.pbclient.find_results(project_id, id=result_id, limit=1,
                                        all=1)[0]
    df = helpers.get_task_run_df(e, result.task_id)

    # Flatten annotations into a single list
    anno_list = df['info'].tolist()
    anno_list = list(itertools.chain.from_iterable(anno_list))
    defaults = {'annotations': []}
    result.info = helpers.init_result_info(doi, path, defaults)
    n_annotations = len(anno_list)
    clusters = []

    # Cluster similar regions
    if n_annotations > 0:
        for anno in anno_list:
            r1 = get_rect_from_selection(anno)
            matched = False
            for cluster in clusters:
                r2 = get_rect_from_selection(cluster)
                overlap_ratio = get_overlap_ratio(r1, r2)
                if overlap_ratio > MERGE_RATIO:
                    matched = True
                    r3 = merge_rects(r1, r2)
                    update_selector(cluster, r3)

            if not matched:
                update_selector(anno, r1)  # still update to round rect params
                clusters.append(anno)

        result.info['annotations'] = clusters

    enki.pbclient.update_result(result)


def analyse_all_selections(**kwargs):
    """Analyse all In the Spotlight selection results."""
    print kwargs
    e = enki.Enki(kwargs['api_key'], kwargs['endpoint'],
                  kwargs['project_short_name'], all=1)
    results = object_loader.load(enki.pbclient.find_results,
                                 project_id=e.project.id, all=1)
    for result in results:
        kwargs['project_id'] = e.project.id
        kwargs['result_id'] = result.id
        print kwargs
        analyse_selections(**kwargs.copy())
