import { JupyterFrontEnd } from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { PartialJSONObject } from '@lumino/coreutils';

import { find } from '@lumino/algorithm';

import { Widget } from '@lumino/widgets';

class DocsAnchorWidget extends Widget {
  constructor() {
    super();

    this.hyperlink = document.createElement('a');
    this.hyperlink.text = 'OpenSARlab Docs';
    this.hyperlink.href = 'https://opensarlab-docs.asf.alaska.edu';
    this.hyperlink.target = 'blank';
    this.addClass('opensarlab-doc-link-widget');
    this.addClass('opensarlab-frontend-object');

    this.node.appendChild(this.hyperlink);
  }

  readonly hyperlink: HTMLAnchorElement;
}

export async function main(
  app: JupyterFrontEnd,
  allSettings: ISettingRegistry.ISettings
): Promise<void> {
  const settings =
    (allSettings.get('doc_link').composite as PartialJSONObject) ??
    (allSettings.default('doc_link') as PartialJSONObject);

  const enabled = settings.enabled as boolean;
  const rank = settings.rank as number;

  const widget_id = 'opensarlab-doc-link-widget';

  const widget = find(app.shell.widgets('top'), w => w.id === widget_id);
  if (widget) {
    widget.dispose();
  }

  if (!enabled) {
    console.log(
      'JupyterLab extension opensarlab-frontend:doc_link is not activated!'
    );
    return;
  }

  const docLinkWidget = new DocsAnchorWidget();
  docLinkWidget.id = widget_id;
  app.shell.add(docLinkWidget as any, 'top', { rank: rank });

  console.log(
    'JupyterLab extension opensarlab-frontend:doc_link is activated!'
  );
}
