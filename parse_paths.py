# -*- coding: utf-8 -*-
'''
svakulenko
29 Mar 2018

Parse shortest paths into subgraphs and collect stats:

print len(set(nodes)), 'nodes in the dialogue graph'
print len(set(edges)), 'edges in the dialogue graph'
# length of the shortest paths stats: min max mean
print min(paths_lengths), 'min length of the shortest paths'
print np.mean(paths_lengths), 'mean length of the shortest paths'
print max(paths_lengths), 'max length of the shortest paths'


Results on 6,480 annotated dialogue graphs (lines):
(1 Error parsing)

Size of the graph:
#nodes in the dialogue graph
    min: 4 mean: 27 max: 215
#edges in the dialogue graph
    min: 3 mean: 40 max: 394
#paths in the dialogue graph
    min: 5 mean: 20 max: 255

#nodes per path
min: 0 mean: 1.08736 max: 3
#edges per path
min: 0 mean: 1.64763 max: 4

#nodes per new entity (every 5 paths)
TODO
#edges per new entity (every 5 paths)
TODO

#anchor entities in the dialogue graph
    min: 1 mean: 4 max: 51

min length of the shortest paths
    min: 1 mean: 2.788 max: 6
mean length of the shortest paths
    min: 2.4 mean: 4.45686 max: 6
max length of the shortest paths
    min: 3 mean: 4 max: 7


'''
import os
from collections import Counter
import json
import numpy as np
from annotate_shortest_paths import PATH_SHORTEST_PATHS


def parse_paths_folder(endpoint='widipedia', nfiles=10):
    '''
    Show most common relations and external entities

    endpoint: dbpedia, widipedia
    nfiles <int> limit the number of files to parse
    '''
    # sample: '' - positive, '_random', '_disorder', '_distribution', '_vertical', '_horizontal'
    # for sample in ['', '_random', '_disorder', '_distribution', '_vertical', '_horizontal']:
    for sample in ['_random']:
        print sample
        
        folder='top5%s_%s/' % (sample, endpoint)

        mentions = Counter()
        nodes = Counter()
        edges = Counter()
        min_distances = Counter()

        files = os.listdir(folder)
        print len(files), 'files'

        n_most_common = 20

        for file_name in files[:nfiles]:
            print file_name
            with open(folder + file_name, 'r') as paths_file:
                lines = paths_file.readlines()
                print len(lines), 'lines'

                for line in lines:
                    try:
                        path_annotation = json.loads(line)
                        # mentioned entities: strip prefix
                        entities = [entity.split('/')[-1] for entity in path_annotation['entities']]
                        mentions.update(entities)
                        min_paths_lengths = []
                        for entity_paths in path_annotation['top5_paths']:
                            entity_paths_lengths = []
                            for path in entity_paths:
                                if path:
                                    hops = path[1:-1].split('-<')
                                    # print hops
                                    nhops = len(hops) - 1 # path length
                                    entity_paths_lengths.append(nhops)
                                    start_node = hops[0]
                                    for hop in hops[1:]:
                                        edge_label, next_node = hop.split('>-')
                                        edges[edge_label] += 1
                                        if next_node not in entities:
                                            nodes[next_node] += 1
                                        start_node = next_node
                            if entity_paths_lengths:
                                min_distance = min(entity_paths_lengths)
                            else:
                                min_distance = float("inf")
                            min_paths_lengths.append(min_distance)
                        min_distances.update(min_paths_lengths)
                    except:
                        print "Error parsing"
                        continue
            # print "Mentioned entities"
            # print mentions.most_common(n_most_common)
            # print "Context (non-mentioned) entities"
            # print nodes.most_common(n_most_common)
            # print "Relations"
            # print edges.most_common(n_most_common)
        print min_distances


def parse_paths(path=PATH_SHORTEST_PATHS, nlines=20000000):
    '''
    nlines <int> limit the number of dialogues (lines) to parse
    '''
    # collect a number of stats for the dialogue graphs
    n_dialogues = 0  # count the number of dialogues managed to parse
    n_nodes = []
    n_edges = []
    n_paths = []
    nodes_per_path = []
    edges_per_path = []
    min_paths_lengths = []
    mean_paths_lengths = []
    max_paths_lengths = []

    metrics = {'nodes in the dialogue graph': n_nodes,
               'edges in the dialogue graph': n_edges,
               'paths in the dialogue graph': n_paths,
               '#nodes per path': nodes_per_path,
               '#edges per path': edges_per_path,
                # length of the shortest paths stats: min max mean
               'min length of the shortest paths': min_paths_lengths,
               'mean length of the shortest paths': mean_paths_lengths,
               'max length of the shortest paths': max_paths_lengths}

    with open(path, 'r') as paths_file:
        for line in paths_file.readlines()[:nlines]:
            # skip dialogues with parsing errors
            try:
                # process 1 dialogue per line
                nodes = []
                edges = []
                paths_lengths = []  # collect distribution of the length of the shortest paths

                parse = line.split('\t')
                file = parse[0]
                # print file, 'dialogue'
                paths = parse[1:]
                for path in paths:
                    hops = path[1:-1].split('-<')
                    nhops = len(hops)  # path length
                    paths_lengths.append(nhops)
                    start_node = hops[0]
                    nodes.append(start_node)
                    for hop in hops[1:]:
                        edge_label, next_node = hop.split('>-')
                        nodes.append(next_node)
                        edges.append((start_node, next_node))
                        start_node = next_node
                
                n_nodes.append(len(set(nodes)))
                n_edges.append(len(set(edges)))
                n_paths.append(len(paths))
                min_paths_lengths.append(min(paths_lengths))
                mean_paths_lengths.append(np.mean(paths_lengths))
                max_paths_lengths.append(max(paths_lengths))
            except:
                print "Error parsing"
                continue

    # derivative metrics final
    nodes_per_path.extend(np.divide(n_nodes, n_paths))
    edges_per_path.extend(np.divide(n_edges, n_paths))

    # analyze the distribution for each of the metric (stats)
    report = "min: %f mean: %f max: %f"
    for metric_name, metric in metrics.items():
        print metric_name
        print report % (min(metric), np.mean(metric), max(metric))


if __name__ == '__main__':
     parse_paths_folder()
