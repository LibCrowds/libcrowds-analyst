# -*- coding: utf8 -*-
"""In the Spotlight analysis module."""

import datetime
import itertools
import enki
from libcrowds_analyst.analysis import helpers


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
        'x': int(regions[0]),
        'y': int(regions[1]),
        'w': int(regions[2]),
        'h': int(regions[3])
    }


def merge_rects(r1, r2):
    """Merge two rectangles."""
    return {
        'x': min(r1['x'], r2['x']),
        'y': min(r1['y'], r2['y']),
        'w': max(r1['x'] + r1['w'], r2['x'] + r2['w']) - r2['x'],
        'h': max(r1['y'] + r1['h'], r2['y'] + r2['h']) - r2['y']
    }


def analyse_selections(api_key, endpoint, project_id, result_id,
                       project_short_name, **kwargs):
    """Analyse In the Spotlight results."""
    e = enki.Enki(api_key, endpoint, project_short_name, all=1)
    result = enki.pbclient.find_results(project_id, id=result_id, limit=1,
                                        all=1)[0]
    df = helpers.get_task_run_df(e, result.task_id)

    # Flatten annotations into a single list
    anno_list = df['info'].tolist()
    anno_list = list(itertools.chain.from_iterable(anno_list))

    result.info = {
        'annotations': anno_list,
        'analysis_complete': True
    }
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
                    r2 = merge_rects(r1, r2)
                    frag = '?xywh={0},{1},{2},{3}'.format(r2['x'], r2['y'],
                                                          r2['w'], r2['h'])
                    cluster['target']['selector']['value'] = frag
                    cluster['modified'] = datetime.datetime.now().isoformat()

            if not matched:
                clusters.append(anno)

        result.info['annotations'] = clusters

    print clusters

    enki.pbclient.update_result(result)
