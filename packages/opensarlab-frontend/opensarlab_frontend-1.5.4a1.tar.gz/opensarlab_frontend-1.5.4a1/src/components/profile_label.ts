import { JupyterFrontEnd } from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { PartialJSONObject } from '@lumino/coreutils';

import { find } from '@lumino/algorithm';

import { Widget } from '@lumino/widgets';

import { requestAPI } from './handler';

class OpensarlabProfileLabelWidget extends Widget {
  constructor() {
    super();

    this.span = document.createElement('span');
    this.addClass('opensarlab-profile-label-widget');
    this.addClass('opensarlab-frontend-object');
    this.node.appendChild(this.span);
  }

  readonly span: HTMLSpanElement;
}

export async function main(
  app: JupyterFrontEnd,
  allSettings: ISettingRegistry.ISettings
): Promise<void> {
  const settings =
    (allSettings.get('profile_label').composite as PartialJSONObject) ??
    (allSettings.default('profile_label') as PartialJSONObject);

  const enabled = settings.enabled as boolean;
  const rank = settings.rank as number;

  const widget_id = 'opensarlab-profile-label-widget';

  const widget = find(app.shell.widgets('top'), w => w.id === widget_id);
  if (widget) {
    widget.dispose();
  }

  if (!enabled) {
    console.log(
      'JupyterLab extension opensarlab-frontend:profile_label is not activated!'
    );
    return;
  }

  try {
    const data = await requestAPI<any>('opensarlab-profile-label');

    const opensarlabProfileLabelWidget = new OpensarlabProfileLabelWidget();
    opensarlabProfileLabelWidget.id = widget_id;
    opensarlabProfileLabelWidget.span.innerText = data['data'];

    app.shell.add(opensarlabProfileLabelWidget as any, 'top', { rank: rank });

    console.log(
      'JupyterLab extension opensarlab-frontend:profile_label is activated!'
    );
  } catch (reason) {
    console.error(
      `Error on GET /opensarlab-frontend/opensarlab-profile-label.\n${reason}`
    );
  }
}
