import { JupyterFrontEnd } from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { PartialJSONObject } from '@lumino/coreutils';

import { find } from '@lumino/algorithm';

import { ToolbarButton } from '@jupyterlab/apputils';

export async function main(
  app: JupyterFrontEnd,
  allSettings: ISettingRegistry.ISettings
): Promise<void> {
  const settings =
    (allSettings.get('gifcap_btn').composite as PartialJSONObject) ??
    (allSettings.default('gifcap_btn') as PartialJSONObject);

  const enabled = settings.enabled as boolean;
  const rank = settings.rank as number;

  const widget_id = 'opensarlab-frontend-gitcap-btn';

  const widget = find(app.shell.widgets('top'), w => w.id === widget_id);
  if (widget) {
    widget.dispose();
  }

  if (!enabled) {
    console.log(
      'JupyterLab extension opensarlab-frontend:gifcap_btn is not activated!'
    );
    return;
  }

  const gifcapBtn = new ToolbarButton({
    className: 'opensarlab-gitcap-btn',
    label: 'GIF Capture',
    onClick: () => {
      window.open('https://gifcap.dev', '_blank');
    },
    tooltip: 'Create and download screen capture GIFs'
  });

  gifcapBtn.id = widget_id;
  gifcapBtn.addClass('opensarlab-frontend-object');

  app.shell.add(gifcapBtn as any, 'top', { rank: rank });

  console.log(
    'JupyterLab extension opensarlab-frontend:gifcap_btn is activated!'
  );
}
