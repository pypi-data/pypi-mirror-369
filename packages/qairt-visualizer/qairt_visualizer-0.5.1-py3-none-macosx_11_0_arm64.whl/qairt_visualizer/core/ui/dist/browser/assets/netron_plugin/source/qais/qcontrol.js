/*
* =============================================================================
*
*  Copyright (c) 2023-2024 Qualcomm Technologies, Inc.
*  All Rights Reserved.
*  Confidential and Proprietary - Qualcomm Technologies, Inc.
*
* ==============================================================================
*/

const qcontrol = {};

qcontrol.init = class {

  static hidePanels() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
      sidebar.style.visibility = 'hidden';
    }
    this.setView();
  }

  static hideControls() {
    const menuButton = document.getElementById('menu-button');
    const toolbar = document.getElementById('toolbar');
    menuButton.style.visibility = 'hidden';
    toolbar.style.visibility = 'hidden';
  }


  static hideSearchField() {
    const searchField = document.getElementById('search');
    if (searchField) {
      searchField.style.visibility = 'hidden';
    }
    // Hide the find sidebar
    this.hidePanels();
  }

  static setView() {
    const container = document.getElementById('graph');
    if (container) {
      container.style.width = '100%';
      container.focus();
    }
  }

  static highlightNode(nodeId) {
    this.unHighlightNode();
    const node = document.getElementById(nodeId);
    node.classList.add('select');
  }

  static unHighlightNode() {
    const nodes = document.querySelectorAll('.graph-node.select, .edge-path.select, .graph-input.select, .graph-output.select');
    for (const node of nodes) {
      node.classList.remove('select');
    }
  }

  static loadGraph(data) {
    if (data) {
      let graphIndex = 0;
      if (window.__view__ && data.length > 1) {
        graphIndex = data.findIndex((file) => file.name.toLowerCase().endsWith('.json'));
        const binIndex = data.findIndex((file) => file.name.toLowerCase().endsWith('.bin'));
        window.__view__.binFile = data[binIndex].file;
      }
      const file = data[graphIndex].file;
      window.__view__?._host._open(file, [file]);
    }
  }

};

qcontrol.IframeCommunicationService = class {

  constructor() {
    this.eventListeners = new Map();
  }

  // Initialze communication with QAIS Main
  setListener() {
    window.addEventListener('message', this.handleMessage.bind(this));
  }

  // Remove listeners onDestroy
  removeEventListener(eventType, callback) {
    const listeners = this.eventListeners.get(eventType);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index !== -1) {
        listeners.splice(index, 1);
      }
    }
  }

  // Add listeners to a specific eventType
  addEventListener(eventType, callback) {
    const listeners = this.eventListeners.get(eventType) || [];
    listeners.push(callback);
    this.eventListeners.set(eventType, listeners);
  }

  // Send message to iframe
  sendMessage(message) {
    parent.postMessage(message, window.location.origin);
  }

  // handle message from QAIS Main
  handleMessage(event) {
    const messageType = event.data.event;
    const listeners = this.eventListeners.get(messageType);
    if (listeners) {
      listeners.forEach(listener => listener(event.data.data));
    }
  }
}

qcontrol.messageEmitter = class {

  static emitMessage(event, data) {
    const message = { event, data, iframeId: window.location.href.split('id=').pop() };
    const iframeCommunicationService = new qcontrol.IframeCommunicationService();
    iframeCommunicationService.sendMessage(message);
  }

}


qcontrol.theme = class {

  static applyTheme(scheme) {
    for (const styleSheet of document.styleSheets) {
      for (const rule of styleSheet.cssRules) {
        if (rule && rule.media && rule.media.mediaText.includes('prefers-color-scheme')) {

          if (scheme === 'dark') {
            // Always use dark irrespective of the system theme
            rule.media.appendMedium('(prefers-color-scheme: dark)');
            rule.media.appendMedium('(prefers-color-scheme: light)');
          }

          if (scheme === 'light') {
            // Use default colors for light theme
            if (rule.media.mediaText.includes('dark')) {
              rule.media.deleteMedium('(prefers-color-scheme: dark)');
            }

            if (rule.media.mediaText.includes('light')) {
              rule.media.deleteMedium('(prefers-color-scheme: light)');
            }

            rule.media.appendMedium('default-prefers-color-scheme');
          }
          // Note: System theme is handled through prefers-color-scheme media query
        }
      }
    }
  }
}

qcontrol.longTextView = class {

  constructor(host, value, action) {
    this._value = value;
    this._host = host;
    this._elements = [];
    this._action = value;

    const element = this._host.document.createElement('div');
    element.className = 'sidebar-item-value';
    this._elements.push(element);
    this._itemValue = element;

    // To show contents in expander
    if (this._value.length > 20) {
      this._expander = this._host.document.createElement('div');
      this._expander.className = 'sidebar-item-value-expander';
      element.appendChild(this._expander);

      const valueLine = this._host.document.createElement('div');
      valueLine.className = 'sidebar-item-value-line-border';
      valueLine.innerText = this._value;

      this._itemValue.appendChild(valueLine);
      this._action = action;
    }

    // To show contents as text field
    const line = this._host.document.createElement('div');
    line.className = 'sidebar-item-value-line';
    line.innerText = this._action;
    element.appendChild(line);
  }

  render() {
    return this._elements;
  }

}

export const init = qcontrol.init;
export const IframeCommunicationService = qcontrol.IframeCommunicationService;
export const messageEmitter = qcontrol.messageEmitter;
export const theme = qcontrol.theme;
export const longTextView = qcontrol.longTextView;
