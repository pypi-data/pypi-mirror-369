import styles from './styles.css';
import { version } from './version.js';

(function (global) {
  'use strict';

  // Module-level settings
  let settings = {
    tableSelector: '.frame-display-table',
    minColumnWidth: 30,
    resizerWidth: 8,
    resizerHoverColor: 'rgba(0,0,0,0.1)',
    showHoverEffect: true,
    autoInit: true,
    allowReInit: false,
    ...(global.FrameDisplayConfig || {}), // merge any global config
  };

  // Prevent multiple executions
  if (global.FrameDisplay) {
    const existingVersion = global.FrameDisplay.version || '0.0.0';

    if (settings.allowReInit === true || version.localeCompare(existingVersion, undefined, { numeric: true }) > 0) {
      // Clean up previous instance and continue
      global.FrameDisplay.destroy();
    } else {
      // Default behavior
      return;
    }
  }

  let observer = null;

  // ------------ STYLES ------------
  function injectStyles() {
    if (document.getElementById('frame-display-styles')) {
      return;
    }
    const style_el = document.createElement('style');
    style_el.id = 'frame-display-styles';
    style_el.textContent = styles;
    document.head.appendChild(style_el);
  }

  // ------------ CORE FUNCTIONALITY ------------
  function addColumnResizing(table) {
    const headers = table.querySelectorAll('thead th');
    headers.forEach((header, index) => {
      if (header.querySelector('.column-resizer')) return;

      // Create resizer element
      const resizer = document.createElement('div');
      resizer.className = 'column-resizer';
      Object.assign(resizer.style, {
        position: 'absolute',
        top: '0',
        right: '0',
        width: settings.resizerWidth + 'px',
        height: '100%',
        cursor: 'col-resize',
        zIndex: '20'
      });

      header.appendChild(resizer);

      // Add hover effect if enabled
      if (settings.showHoverEffect) {
        resizer.addEventListener('mouseover', () => {
          resizer.style.backgroundColor = settings.resizerHoverColor;
        });
        resizer.addEventListener('mouseout', () => {
          resizer.style.backgroundColor = '';
        });
      }

      // Prevent sort on resizer click
      resizer.addEventListener('click', function (e) {
        e.stopPropagation();
      });

      // Resize functionality
      let startX, startWidth;
      resizer.addEventListener('pointerdown', function (e) {
        startX = e.clientX;
        startWidth = parseFloat(window.getComputedStyle(header).width);

        resizer.setPointerCapture(e.pointerId);
        resizer.addEventListener('pointermove', handleResize);
        resizer.addEventListener('pointerup', stopResize, { once: true });

        table.classList.add('resizing');
        document.body.style.userSelect = 'none';
        e.preventDefault();
        e.stopPropagation();
      });

      function handleResize(e) {
        const newWidth = Math.max(settings.minColumnWidth, startWidth + (e.clientX - startX));
        // Update the header cell width
        header.style.setProperty('width', newWidth + 'px', 'important');
        header.style.setProperty('min-width', newWidth + 'px', 'important');

        // Scroll to keep header's right edge at container's right edge
        const container = table.closest('.table-container');
        if (container) {
          const headerRect = header.getBoundingClientRect();
          const containerRect = container.getBoundingClientRect();

          // If header extends beyond visible area, scroll to align right edges
          const overshoot = headerRect.right - containerRect.right;
          if (overshoot > 0) {
            container.scrollLeft += overshoot;
          }
        }

        if (header.getAttribute("data-released") != "true") {
          header.style.setProperty('max-width', 0);
          header.setAttribute("data-released", "true");
          const colIndex = index + 1; // 1-based for CSS selector
          // Expensive, but only done once per column resize
          // I couldn't find a workaround to avoid this
          table.querySelectorAll(`td:nth-child(${colIndex})`).forEach(cell => {
            cell.style.setProperty('max-width', 0);
          });
        }
      }

      function stopResize(e) {
        e.stopPropagation();
        e.preventDefault();
        resizer.releasePointerCapture(e.pointerId);
        resizer.removeEventListener('pointermove', handleResize);
        resizer.removeEventListener('pointerup', stopResize);
        document.body.style.userSelect = '';
        setTimeout(() => table.classList.remove('resizing'), 0);
      }
    });
  }

  function addTooltips(table) {
    table.querySelectorAll('th, td').forEach(cell => {
      const text = cell.textContent.trim();
      if (text) {
        cell.title = text; // Show full text on hover
      }
    });
  }

  function addSorting(table) {
    // Add click handlers to data headers (skip first - it's the index column)
    table.querySelectorAll('thead th').forEach((th, colIndex) => {
      th.addEventListener('dblclick', (e) => {
        e.preventDefault(); // Prevent double-click text selection
      });
      th.addEventListener('click', () => {
        if (table.classList.contains('resizing')) {
          return; // Ignore clicks during resizing
        }
        sortColumn(table, colIndex + 1, th);
      });
    });
  }

  function sortColumn(table, colIndex, header) {
    const sortData = table.dataset.sort || '1-asc';
    const [currentCol, currentState] = sortData.split('-');
    const currentColNum = parseInt(currentCol);

    // Determine next state for this column
    const nextState = (currentColNum === colIndex && currentState === 'asc') ? 'desc' :
      (currentColNum === colIndex && currentState === 'desc') ? 'none' : 'asc';

    // Clear previous sort indicator
    if (currentColNum !== colIndex) {
      const prevHeader = table.querySelector(`thead th:nth-child(${currentColNum})`);
      if (prevHeader) clearSortIndicator(prevHeader);
    }

    table.dataset.sort = `${colIndex}-${nextState}`;
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    if (nextState === 'none') {
      // Sort by index column to restore original order
      const sortedRows = sortRowsByColumn(rows, 1, 'asc', 'object');
      sortedRows.forEach(row => tbody.appendChild(row));
    } else {
      const sortedRows = sortRowsByColumn(rows, colIndex, nextState, header.dataset.dtype);
      sortedRows.forEach(row => tbody.appendChild(row));
    }

    updateSortIndicator(header, nextState);
  }

  function updateSortIndicator(header, state) {
    clearSortIndicator(header);
    if (state !== 'none') {
      header.classList.add(`sort-${state}`);
    }
  }

  function clearSortIndicator(header) {
    header.classList.remove('sort-asc', 'sort-desc');
  }

  function sortRowsByColumn(rows, colIndex, direction, dtype) {
    const rowData = rows.map(row => {
      const cell = row.querySelector(`td:nth-child(${colIndex}), th:nth-child(${colIndex})`);
      const isNull = cell?.querySelector('.null-cell');
      const rawValue = cell?.textContent.trim() || '';

      let sortValue = rawValue;
      if (!isNull && rawValue) {
        switch (dtype) {
          case 'int':
          case 'float':
            sortValue = parseFloat(rawValue) || rawValue;
            break;
          case 'datetime':
            sortValue = new Date(rawValue).getTime() || rawValue;
            break;
          case 'bool':
            sortValue = /^(true|1|yes|on|t|y)$/i.test(rawValue) ? 1 : 0;
            break;
          default:
            if (colIndex === 1) { // Index column
              sortValue = parseFloat(rawValue) || rawValue;
            }
        }
      }

      return { row, isNull, sortValue };
    });

    return rowData
      .sort((a, b) => {
        if (a.isNull !== b.isNull) return a.isNull ? 1 : -1;

        const result = typeof a.sortValue === 'number'
          ? a.sortValue - b.sortValue
          : a.sortValue.localeCompare(b.sortValue, undefined, { numeric: true, sensitivity: 'base' });

        return direction === 'asc' ? result : -result;
      })
      .map(item => item.row);
  }

  function processTable(table) {
    if (table.hasAttribute('data-initialized')) {
      return;
    }
    addColumnResizing(table);
    addTooltips(table);
    addSorting(table);
    table.setAttribute('data-initialized', 'true');
  }

  // ------------ PUBLIC API ------------
  function setup(config = {}) {
    injectStyles();
    // Update module-level settings
    settings = {
      ...settings,
      ...config
    };
    document.querySelectorAll(settings.tableSelector).forEach(processTable);
  }

  function destroy() {
    if (observer) {
      observer.disconnect();
      observer = null;
    }
    // Find and clean up all processed tables
    document.querySelectorAll('.frame-display-table[data-initialized]').forEach(table => {
      // Clean up resizers
      table.querySelectorAll('.column-resizer').forEach(resizer => {
        resizer.remove();
      });

      // Clean up sorting
      table.querySelectorAll('thead th').forEach(th => {
        const newTh = th.cloneNode(true); // to remove event listeners
        th.parentNode.replaceChild(newTh, th);
        newTh.classList.remove('sort-asc', 'sort-desc');
      });

      if (table.dataset.sort) {
        delete table.dataset.sort;
      }

      table.removeAttribute('data-initialized');
      table.classList.remove('resizing');
    });

    const styleElement = document.getElementById('frame-display-styles');
    if (styleElement) {
      styleElement.remove();
    }

    if (global.FrameDisplay) {
      delete global.FrameDisplay;
    }

    return true;
  }

  // ------------ JUPYTER SUPPORT ------------
  function createTableWatcher() {
    if (typeof MutationObserver === 'undefined') return;

    observer = new MutationObserver((mutations) => {
      mutations.forEach(mutation => {
        // Only process added nodes
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
          mutation.addedNodes.forEach(node => {
            // Check if the node itself is a table or contains tables
            if (node.nodeType === Node.ELEMENT_NODE) {
              const tables = [];
              if (node.matches && node.matches('.frame-display-table')) {
                tables.push(node);
              }
              tables.push(...node.querySelectorAll('.frame-display-table:not([data-initialized])'));

              tables.forEach(processTable);
            }
          });
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    return observer;
  }

  // ------------ AUTO-SETUP LOGIC ------------
  function setupOnLoad() {
    // Check if auto-setup is disabled
    if (settings.autoInit === false) {
      return;
    }
    // Auto-setup with global config
    setup();
    // Also watch for new tables being added
    createTableWatcher();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupOnLoad);
  } else {
    setTimeout(setupOnLoad, 0);
  }

  // ------------ EXPORTS ------------
  global.FrameDisplay = {
    setup: setup,
    destroy: destroy,
    version: version,
  };
})(typeof window !== 'undefined' ? window : this);
