/*
* =============================================================================
*
*  Copyright (c) 2023-2024 Qualcomm Technologies, Inc.
*  All Rights Reserved.
*  Confidential and Proprietary - Qualcomm Technologies, Inc.
*
* ==============================================================================
*/
import * as qcontrol from './qcontrol.js';

const iframeCommunicationService = new qcontrol.IframeCommunicationService();
iframeCommunicationService.setListener();

const qsubgraph = class {

  static EDGE_DIRECTIONS = {
    INCOMING: 'incoming',
    OUTGOING: 'outgoing'
  };

  static async confirmSubgraphSize() {
    const waitForDialogConfirmation = () => {
      return new Promise((resolve) => {
        const handleSubmitMessage = (data) => {
          iframeCommunicationService.removeEventListener('subgraph_dialog_submit', handleSubmitMessage);
          resolve(data);
        };
        iframeCommunicationService.addEventListener('subgraph_dialog_submit', handleSubmitMessage);
      });
    };

    qcontrol.messageEmitter.emitMessage('subgraph_dialog_show');
    return await waitForDialogConfirmation();
  }

  static createEdgeLookups(edges) {
    const [incomingEdgesLookup, outgoingEdgesLookup] = [new Map(), new Map()];

    edges.forEach((edgeVal, edgeKey) => {
      const { to, from } = edgeVal.label;
      const edge = { edgeKey, edgeVal };

      if (!incomingEdgesLookup.has(to.id)) {
        incomingEdgesLookup.set(to.id, []);
      }
      incomingEdgesLookup.get(to.id).push(edge);

      if (!outgoingEdgesLookup.has(from.id)) {
        outgoingEdgesLookup.set(from.id, []);
      }
      outgoingEdgesLookup.get(from.id).push(edge);
    });

    return {
      [this.EDGE_DIRECTIONS.INCOMING]: incomingEdgesLookup,
      [this.EDGE_DIRECTIONS.OUTGOING]: outgoingEdgesLookup
    };
  }

  static findById(items, id) {
    for (const [_, itemVal] of items) {
      if (itemVal.label.id === id) {
        return itemVal;
      }
    }
  }

  static findStartNode(graph) {
    const { startNodeId } = graph.view;
    if (startNodeId) {
      return this.findById(graph.nodes, startNodeId);
    }
    const firstNode = graph.nodes.values().next().value;
    return firstNode;
  }

  static buildGraphBFS(graph, subgraphNodes, subgraphEdges, edgeLookups) {
    let nodeCount = 0;
    const visited = new Set();
    const queue = [];

    const startNode = this.findStartNode(graph);
    queue.push(startNode);
    visited.add(startNode.v);
    nodeCount++;

    const enqueueNeighbors = (node, edgeDirection) => {
      const edges = edgeLookups[edgeDirection].get(node.label.id) || [];
      if (nodeCount < graph.view.subgraphSize) {
        for (const { edgeKey, edgeVal } of edges) {
          subgraphEdges.set(edgeKey, edgeVal);
          const neighbor = edgeDirection === this.EDGE_DIRECTIONS.INCOMING ? edgeVal.label.from : edgeVal.label.to;
          if (!visited.has(neighbor.name)) {
            const neighborNode = { v: neighbor.name, label: neighbor };
            queue.push(neighborNode);
            visited.add(neighborNode.v);
            nodeCount++;
          }
        }
      } else if (edges.length) {
        const hasHiddenEdges = edges.some(({ edgeKey }) => !subgraphEdges.has(edgeKey));
        if (hasHiddenEdges) {
          if (!node.label.hiddenEdgesDirections) {
            node.label.hiddenEdgesDirections = new Set();
          }
          node.label.hiddenEdgesDirections.add(edgeDirection);
        }
      }
    };

    while (queue.length) {
      const node = queue.shift();
      subgraphNodes.set(node.v, node);

      enqueueNeighbors(node, this.EDGE_DIRECTIONS.OUTGOING);
      enqueueNeighbors(node, this.EDGE_DIRECTIONS.INCOMING);
    }
  }

  static orderNodes(nodes) {
    return new Map([...nodes.entries()].sort((a, b) => Number(a[0]) - Number(b[0])));
  }

  static orderEdges(edges) {
    return new Map([...edges.entries()].sort((a, b) => {
      const [aFromNode, aToNode] = a[0].split(':');
      const [bFromNode, bToNode] = b[0].split(':');
      if (aFromNode === bFromNode) {
        return Number(aToNode) - Number(bToNode);
      }
      return Number(aFromNode) - Number(bFromNode)
    }));
  }

  static createSubgraph(graph) {
    const edgeLookups = this.createEdgeLookups(graph.edges);
    const [subgraphNodes, subgraphEdges] = [new Map(), new Map()];

    this.buildGraphBFS(graph, subgraphNodes, subgraphEdges, edgeLookups);

    graph.fullNodes = graph.nodes;
    graph.fullEdges = graph.edges;
    graph.nodes = this.orderNodes(subgraphNodes);
    graph.edges = this.orderEdges(subgraphEdges);
    graph.selectionIdLookup = new Set();
    graph.edgeLookup = new Map();
    subgraphNodes.forEach(node => graph.selectionIdLookup.add(node.label.id));
    subgraphEdges.forEach(edge => graph.selectionIdLookup.add(edge.label.id));
    graph.fullEdges.forEach(edge => graph.edgeLookup.set(edge.label.id, edge));
  }

  static async renderGraph(view, node) {
    view.startNodeId = node.id;
    const { model, activeGraph, options } = view;
    await view.renderGraph(model, activeGraph, null, options);
  }

  static async renderGraphAndSelectNode(view, node) {
    await this.renderGraph(view, node);
    const element = document.getElementById(node.id);
    view.scrollTo([element]);
    view.showNodeProperties(node);
  }

  static renderHiddenEdgesMarkers(node) {
    const view = node.context.view;
    const markerRadius = 5;

    const renderMarker = (x, y, direction) => {
      const markerGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      markerGroup.setAttribute('x', x);
      markerGroup.setAttribute('y', y);
      markerGroup.setAttribute('class', 'hidden-edges-marker');
      markerGroup.addEventListener('click', () => this.renderGraphAndSelectNode(view, node.value));

      const marker = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      marker.setAttribute('r', markerRadius);
      marker.setAttribute('cx', x);
      marker.setAttribute('cy', y);
      markerGroup.appendChild(marker);

      const plusSignGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      plusSignGroup.setAttribute('class', 'hidden-edges-marker-plus');
      const lineLength = 3;
      const verticalLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      verticalLine.setAttribute('x1', x);
      verticalLine.setAttribute('x2', x);
      verticalLine.setAttribute('y1', y - lineLength);
      verticalLine.setAttribute('y2', y + lineLength);

      const horizontalLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      horizontalLine.setAttribute('x1', x - lineLength);
      horizontalLine.setAttribute('x2', x + lineLength);
      horizontalLine.setAttribute('y1', y);
      horizontalLine.setAttribute('y2', y);
      plusSignGroup.appendChild(horizontalLine);
      plusSignGroup.appendChild(verticalLine);
      markerGroup.appendChild(plusSignGroup);

      const tooltip = document.createElementNS('http://www.w3.org/2000/svg', 'title');
      tooltip.textContent = `There are ${direction} edges not displayed in this subgraph. Click to render the ${view.subgraphSize} nodes nearest this one to see a different part of the graph.`;
      markerGroup.appendChild(tooltip);

      node.element.appendChild(markerGroup);
    };

    if (node.hiddenEdgesDirections?.has(this.EDGE_DIRECTIONS.INCOMING)) {
      renderMarker(node.width / 2, -markerRadius / 2, this.EDGE_DIRECTIONS.INCOMING);
    }
    if (node.hiddenEdgesDirections?.has(this.EDGE_DIRECTIONS.OUTGOING)) {
      renderMarker(node.width / 2, node.height + markerRadius / 2, this.EDGE_DIRECTIONS.OUTGOING);
    }
  }

  static async renderSubgraph(selection, graph) {
    const isSelectionInSubgraph = graph.selectionIdLookup.has(selection.id);
    if (!isSelectionInSubgraph) {
      const isEdgeSelected = selection.id.startsWith('edge-');
      const startNode = isEdgeSelected ? graph.edgeLookup.get(selection.id).label.from : selection;
      await this.renderGraph(graph.view, startNode);
    }
  }
};

export default qsubgraph;
