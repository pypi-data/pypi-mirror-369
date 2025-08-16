import { JupyterFrontEnd } from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { PartialJSONObject } from '@lumino/coreutils';

import { find } from '@lumino/algorithm';

import { ToolbarButton } from '@jupyterlab/apputils';

import { requestAPI } from './handler';

export async function main(
  app: JupyterFrontEnd,
  allSettings: ISettingRegistry.ISettings
): Promise<void> {
  const settings =
    (allSettings.get('controlbtn').composite as PartialJSONObject) ??
    (allSettings.default('controlbtn') as PartialJSONObject);

  const enabled = settings.enabled as boolean;
  const rank = settings.rank as number;

  const widget_id = 'opensarlab-controlbtn';

  const widget = find(app.shell.widgets('top'), w => w.id === widget_id);
  if (widget) {
    widget.dispose();
  }

  if (!enabled) {
    console.log(
      'JupyterLab extension opensarlab-frontend:controlbtn is not activated!'
    );
    return;
  }

  try {
    const data = await requestAPI<any>('opensarlab-controlbtn');

    const serverBtn = new ToolbarButton({
      className: 'opensarlab-controlbtn',
      label: 'Shutdown and Logout Page',
      onClick: () => {
        window.location.href = data['data'];
      },
      tooltip: 'Hub Control Panel: A place to stop the server and logout'
    });
    serverBtn.id = widget_id;
    serverBtn.addClass('opensarlab-frontend-object');

    app.shell.add(serverBtn as any, 'top', { rank: rank });

    console.log(
      'JupyterLab extension opensarlab-frontend:controlbtn is activated!'
    );
  } catch (reason) {
    console.error(
      `Error on GET /opensarlab-frontend/opensarlab-controlbtn.\n${reason}`
    );
  }
}
