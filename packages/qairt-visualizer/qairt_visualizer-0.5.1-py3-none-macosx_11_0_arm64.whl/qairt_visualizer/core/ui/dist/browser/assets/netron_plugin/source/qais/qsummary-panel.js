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

const infoControl = () => {
  const message = { event: 'info_control', data: fetchProperties() };
  iframeCommunicationService.sendMessage(message);
}

const fetchProperties = () => {
  const sidebarContentEl = document.getElementById('sidebar-content');
  // Create a virtual representation of the sidebar content
  const sidebarObjectEl = sidebarContentEl.querySelector('.sidebar-object');
  const virtualSidebarContent = sidebarObjectEl.cloneNode(true);
  const childElements = virtualSidebarContent.children;
  const groups = [];
  let currentGroup = [];
  let currentKey = 'General'; // collects all the properties that doesnt have headers

  Array.from(childElements).forEach((element) => {
    if (element.classList.contains('sidebar-header')) {
      if (currentGroup.length) {
        groups.push({
          [currentKey]: currentGroup
        });
        currentGroup = [];
      }
      // This holds the header text
      currentKey = element.textContent.trim();
    }
    else if (element.classList.contains('sidebar-item')) {
      const inputElement = element.querySelector('.sidebar-item-name input');
      const key = inputElement ? inputElement.value : '';
      if (key) {
        const content = [];
        
        // iterate to fetch the properties under different headers
        const valueElements = element.querySelectorAll('.sidebar-item-value-list .sidebar-item-value');

        // iterate to fetch the tensor information for each property
        valueElements.forEach((valueElement) => {
          const tensorNameElement = valueElement.querySelector('.sidebar-item-value-line');
          // With recent Netron upgrade, the ability to fetch tensor information when a tensor(edge) is clicked is yet to be added. Until then, ‘NA’ will be passed for names
          // JIRA: AISW-104810
          const tensorName = tensorNameElement?.textContent?.trim() || 'NA';
      
          const tensorInfoElements = valueElement.querySelectorAll('.sidebar-item-value-line-border');
          const tensorInfo = Array.from(tensorInfoElements).filter(el => el.textContent).map((tensorInfoElement) => tensorInfoElement.textContent);
      
          content.push({tensorName, tensorInfo});
      });

        if (content.length) {
          // re-grouping the sub-headers as keys and its contents as property value
          const existingGroup = currentGroup.find((group) => group.hasOwnProperty(key));
          if (existingGroup) {
            existingGroup[key].push(content);
          } else {
            currentGroup.push({
              [key]: content
            });
          }
        }
      }
    }
  });

  // re-grouping the headers as keys and its contents as property value
  if (currentGroup.length) {
    groups.push({
      [currentKey]: currentGroup
    });
  }

  return groups;
}

iframeCommunicationService.addEventListener('info_control', infoControl);
