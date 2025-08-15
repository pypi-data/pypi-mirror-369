/*
* =============================================================================
*
*  Copyright (c) 2023-2024 Qualcomm Technologies, Inc.
*  All Rights Reserved.
*  Confidential and Proprietary - Qualcomm Technologies, Inc.
*
* ==============================================================================
*/

import * as qcontrol from './qcontrol.js';

const iframeCommunicationService = new qcontrol.IframeCommunicationService();
iframeCommunicationService.setListener();

const zoomControl = (data) => {
  if (data === 'zoomIn') {
    window.__view__.zoomIn();
  }

  if (data === 'zoomOut') {
    window.__view__.zoomOut();
  }

  if (data === 'resize') {
    window.__view__.resetZoom();
  }
};

const searchControl = (data) => {
  openSearchBar();
  const searchField = document.getElementById('search');
  const inputEvent = new Event('input');
  searchField.value = data;
  searchField.dispatchEvent(inputEvent);

  const olElement = document.querySelector('ol');
  if (olElement) {
    const liElements = olElement.querySelectorAll('li');
    const liData = Array.from(liElements)
      .map(li => {
        const useElement = li.querySelector('use');
        let icon = '';
        if (useElement) {
          const iconType = useElement.getAttribute('href');
          switch (iconType) {
            case '#sidebar-icon-connection':
              icon = '\u2192';
              break;
            case '#sidebar-icon-node':
              icon = '\u25A2';
              break;
            default:
              icon = '\u25A0';
          }
        }
        return { id: li.getAttribute('id'), value: icon + ' ' + li.textContent };
      });

    const searchValues = { event: 'search', data: liData };
    iframeCommunicationService.sendMessage(searchValues);
  }
}

const openSearchBar = () => {
  const searchField = document.getElementById('search');
  if (!searchField) {
    window.__view__.find();
  }
}

const highlightSearchControl = (id) => {
  openSearchBar()
  // If searching a weight, highlight its associated node
  if (id.startsWith('weight')) {
    id = id.substring(id.indexOf('-') + 1);
  }
  const olElement = document.querySelector('ol');
  if (olElement) {
    const listItems = Array.from(olElement.getElementsByTagName('li'));
    const liElementToHighlight = listItems.find(element => element.getAttribute('id') === id);
    if (liElementToHighlight) {
      const clickEvent = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        view: window
      });

      liElementToHighlight.dispatchEvent(clickEvent);
    } else {
      qcontrol.messageEmitter.emitMessage('property_request', { propertyType: 'node', nodeId: id, nodeNotFound: true });
    }
  }
}

const themeControl = (data) => {
  qcontrol.theme.applyTheme(data);
}

const loadGraph = (data) => qcontrol.init.loadGraph(data);

const fetchOutputToNodeMap = () => {
  const outputToNodeMap = new Map();
  for (const node of window.__view__.activeGraph.nodes) {
    for (const output of node.outputs) {
      for (const outputValue of output.value) {
        outputToNodeMap.set(outputValue.name, node.name);
      }
    }
  }

  iframeCommunicationService.sendMessage({
    event: 'output_to_node_map',
    data: outputToNodeMap,
  });
};

iframeCommunicationService.addEventListener('zoom_controls', zoomControl);
iframeCommunicationService.addEventListener('search', searchControl);
iframeCommunicationService.addEventListener('highlight_search', highlightSearchControl);
iframeCommunicationService.addEventListener('theme_control', themeControl);
iframeCommunicationService.addEventListener('load_graph', loadGraph);
iframeCommunicationService.addEventListener('output_to_node_map', fetchOutputToNodeMap);
