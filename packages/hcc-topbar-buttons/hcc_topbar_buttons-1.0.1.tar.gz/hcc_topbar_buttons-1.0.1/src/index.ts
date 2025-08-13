import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  IRouter,
} from '@jupyterlab/application';

import { IToolbarWidgetRegistry } from '@jupyterlab/apputils';

import '@jupyterlab/application/style/buttons.css';

import { Widget } from '@lumino/widgets';

import '../style/index.css';

const topBarButtonsPlugin = 'jupyterlab-logout:plugin';

export namespace CommandIds {
  export const hdcdocs = 'jupyterlab-topbar:hdcdocs';
  export const controlPanelCmd = 'jupyterlab-topbar:controlpanel';
  export const logoutCmd = 'jupyterlab-topbar:logout';
}

const extension: JupyterFrontEndPlugin<void> = {
  id: topBarButtonsPlugin,
  autoStart: true,
  requires: [IRouter, IToolbarWidgetRegistry],
  activate: async (
    app: JupyterFrontEnd,
    router: IRouter,
    toolbarRegistry: IToolbarWidgetRegistry,
  ): Promise<void> => {
    console.log(
      '%cWelcome to HUNT Workbench!',
      'margin: 12px; color: #00509e; font-weight: bold; font-size: 20px',
    );
    if (window && window.location && window.location.origin) {
      const hubUrl = `${window.location.origin}/hub/home`;
      console.log(
        `%cHub control panel: ${hubUrl}`,
        'margin: 24px 12px 24px 12px; font-size: 14px',
      );
    }
    console.log(
      '%cGetting started: https://docs.hdc.ntnu.no/do-science/hunt-workbench/getting-started/',
      'margin: 24px 12px 24px 12px; font-size: 14px',
    );
    console.log(
      '%cAre you looking for troubleshooting guides?',
      'margin: 12px; color: #00509e; font-weight: bold; font-size: 20px',
    );
    console.log(
      '%chttps://docs.hdc.ntnu.no/do-science/hunt-workbench/troubleshooting/',
      'margin: 24px 12px 24px 12px; font-size: 14px',
    );
    console.log('activating jupyterlab-logout extension');

    app.commands.addCommand(CommandIds.hdcdocs, {
      label: 'Documentation',
      isVisible: () => false,
      execute: (args: any) => {
        window.open(
          'https://docs.hdc.ntnu.no/do-science/hunt-workbench/getting-started/',
          '_blank',
        );
      },
    });

    const docsDivNode = document.createElement('div');
    const docsBtnNode = document.createElement('button');
    const docsSpanNode = document.createElement('span');
    docsSpanNode.id = 'hunt-cloud-documentation';
    docsSpanNode.innerHTML = 'Documentation';
    docsSpanNode.classList.add('jp-ToolbarButtonComponent-label');
    docsBtnNode.setAttribute('title', 'Documentation');
    docsBtnNode.setAttribute('aria-disabled', 'false');
    docsBtnNode.setAttribute('data-command', CommandIds.hdcdocs);
    docsBtnNode.appendChild(docsSpanNode);
    docsBtnNode.addEventListener('click', () => {
      // Redirect without router since redirecting to external URL
      window.open(
        'https://docs.hdc.ntnu.no/do-science/hunt-workbench/getting-started/',
        '_blank',
      );
    });
    ['jp-ToolbarButtonComponent', 'jp-mod-minimal', 'jp-Button'].forEach(
      (item) => {
        docsBtnNode.classList.add(item);
      },
    );
    docsDivNode.appendChild(docsBtnNode);

    toolbarRegistry.addFactory('TopBar', 'hdcdocs', () => {
      const docsDivWidget = new Widget({ node: docsDivNode });
      [
        'lm-Widget',
        'jp-CommandToolbarButton',
        'jp-Toolbar-item',
        'workbench-button',
      ].forEach((item) => {
        docsDivWidget.addClass(item);
      });
      return docsDivWidget;
    });

    app.commands.addCommand(CommandIds.controlPanelCmd, {
      label: 'Control Panel',
      isVisible: () => false,
      execute: (args: any) => {
        let hubUrl = '/hub/home';
        if (window && window.location && window.location.origin) {
          hubUrl = `${window.location.origin}/hub/home`;
          // Redirect without router since redirecting to external URL
          console.log(`Redirecting to ${hubUrl}`);
          window.open(hubUrl, '_blank');
        } else {
          router.navigate(hubUrl, { hard: true });
        }
      },
    });

    const ctrlDivNode = document.createElement('div');
    const ctrlBtnNode = document.createElement('button');
    const ctrlSpanNode = document.createElement('span');
    ctrlSpanNode.id = 'control-panel';
    ctrlSpanNode.innerHTML = 'Control Panel';
    ctrlSpanNode.classList.add('jp-ToolbarButtonComponent-label');
    ctrlBtnNode.setAttribute('title', 'Control Panel');
    ctrlBtnNode.setAttribute('aria-disabled', 'false');
    ctrlBtnNode.setAttribute('data-command', CommandIds.controlPanelCmd);
    ctrlBtnNode.appendChild(ctrlSpanNode);
    ctrlBtnNode.addEventListener('click', () => {
      app.commands.execute(CommandIds.controlPanelCmd);
    });
    ['jp-ToolbarButtonComponent', 'jp-mod-minimal', 'jp-Button'].forEach(
      (item) => {
        ctrlBtnNode.classList.add(item);
      },
    );
    ctrlDivNode.appendChild(ctrlBtnNode);

    toolbarRegistry.addFactory('TopBar', 'controlpanel', () => {
      const ctrlDivWidget = new Widget({ node: ctrlDivNode });
      [
        'lm-Widget',
        'jp-CommandToolbarButton',
        'jp-Toolbar-item',
        'workbench-button',
      ].forEach((item) => {
        ctrlDivWidget.addClass(item);
      });
      return ctrlDivWidget;
    });

    app.commands.addCommand(CommandIds.logoutCmd, {
      label: 'Log Out',
      execute: (args: any) => {
        router.navigate('/logout', { hard: true });
      },
    });

    const lougoutDivNode = document.createElement('div');
    const lougoutBtnNode = document.createElement('button');
    const lougoutSpanNode = document.createElement('span');
    lougoutSpanNode.id = 'logout';
    lougoutSpanNode.innerHTML =
      '<i aria-hidden="true" class="fa fa-sign-out"></i> Logout';
    lougoutSpanNode.classList.add('jp-ToolbarButtonComponent-label');
    lougoutBtnNode.setAttribute('title', 'Logout');
    lougoutBtnNode.setAttribute('aria-disabled', 'false');
    lougoutBtnNode.setAttribute('data-command', CommandIds.logoutCmd);
    lougoutBtnNode.appendChild(lougoutSpanNode);
    lougoutBtnNode.addEventListener('click', () => {
      app.commands.execute(CommandIds.logoutCmd);
    });
    ['jp-ToolbarButtonComponent', 'jp-mod-minimal', 'jp-Button'].forEach(
      (item) => {
        lougoutBtnNode.classList.add(item);
      },
    );
    lougoutDivNode.appendChild(lougoutBtnNode);

    toolbarRegistry.addFactory('TopBar', 'logout', () => {
      const lougoutDivWidget = new Widget({ node: lougoutDivNode });
      [
        'lm-Widget',
        'jp-CommandToolbarButton',
        'jp-Toolbar-item',
        'workbench-button',
      ].forEach((item) => {
        lougoutDivWidget.addClass(item);
      });
      return lougoutDivWidget;
    });

    console.log('jupyterlab-logout extension is activated!');
  },
};

export default extension;
