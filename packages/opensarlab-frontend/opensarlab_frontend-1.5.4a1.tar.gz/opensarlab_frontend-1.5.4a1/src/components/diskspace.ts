import { JupyterFrontEnd } from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { PartialJSONObject } from '@lumino/coreutils';

import { find } from '@lumino/algorithm';

import { Widget } from '@lumino/widgets';

import { requestAPI } from './handler';

class DiskSpaceWidget extends Widget {
  private btyes_to_mb: number;
  private outerDiv: HTMLDivElement;
  private innerDiv: HTMLDivElement;
  private setIntervalKeeper: number;
  private diskSpaceInterval: number;

  constructor(settings: any) {
    super();

    this.btyes_to_mb = 1.0 / (1024 * 1024);
    this.outerDiv = document.createElement('div');
    this.innerDiv = document.createElement('div');
    this.outerDiv.className = 'diskspace';
    this.innerDiv.className = 'diskspace-tooltip-text';
    this.setIntervalKeeper = 0;
    this.diskSpaceInterval = 5000; //ms

    this.addClass('opensarlab-frontend-object');
    this.node.appendChild(this.outerDiv);

    this.checkDiskSpaceInterval(settings);
    this.setIntervalKeeper = window.setInterval(
      this.checkDiskSpaceInterval.bind(this),
      this.diskSpaceInterval,
      settings
    );
  }

  removeSetInterval(): void {
    window.clearInterval(this.setIntervalKeeper);
  }

  async checkDiskSpaceInterval(settings: any): Promise<void> {
    const setCriticalThreshold: number =
      settings.setCriticalThreshold as number;
    const setDangerThreshold: number = settings.setDangerThreshold as number;
    const setWarningThreshold: number = settings.setWarningThreshold as number;
    const diskSpacePath: string = settings.diskSpacePath as string;

    let data: any = await requestAPI<any>(
      `opensarlab-diskspace?path=${diskSpacePath}`
    );

    if (!data) {
      console.warn(
        `No diskspace data returned by API call for path ${diskSpacePath}.`
      );
      return;
    }

    data = data['data'];
    const total: number = data['total'] || null;
    const used: number = data['used'] || null;
    const free: number = data['free'] || null;
    const percentUsed: number = (used / total) * 100;

    let statusColorClass: string = '';
    let statusBlinkClass: string = '';

    if (percentUsed >= setCriticalThreshold) {
      statusColorClass = 'red';
      statusBlinkClass = 'blink-me';
    } else if (percentUsed >= setDangerThreshold) {
      statusColorClass = 'red';
    } else if (percentUsed >= setWarningThreshold) {
      statusColorClass = 'yellow';
    }

    // span gives disk storage percent remaining
    this.outerDiv.innerHTML = `
      <span class="${statusBlinkClass} ${statusColorClass}">
        Disk space used: ${percentUsed.toFixed(2).toString()}%
      </span>
    `;

    // popup gives all the data
    this.innerDiv.innerHTML = `
      <div> Free MB: ${(free / this.btyes_to_mb).toFixed(2)} </div>
      <div> Used MB: ${(used / this.btyes_to_mb).toFixed(2)} </div>
      <div> Total MB: ${(total / this.btyes_to_mb).toFixed(2)} </div>
    `;

    //*** Until the popup renders properly, we are not using it
    /// this.outerDiv.appendChild(this.innerDiv);
  }
}

export async function main(
  app: JupyterFrontEnd,
  allSettings: ISettingRegistry.ISettings
): Promise<void> {
  const settings: PartialJSONObject =
    (allSettings.get('diskspace').composite as PartialJSONObject) ??
    (allSettings.default('diskspace') as PartialJSONObject);

  const enabled: boolean = settings.enabled as boolean;
  const rank: number = settings.rank as number;

  const widget_id: string = 'opensarlab-diskspace-widget';
  const widgetPlacement: string = 'top';

  const opensarlabdiskspaceWidget: any = find(
    app.shell.widgets(widgetPlacement),
    w => w.id === widget_id
  );
  if (opensarlabdiskspaceWidget) {
    // If disposing of widget, remove setInterval manually since it is part of window and not widget
    opensarlabdiskspaceWidget.removeSetInterval();
    opensarlabdiskspaceWidget.dispose();
  }

  if (!enabled) {
    console.log(
      'JupyterLab extension opensarlab-frontend:diskspace is not activated!'
    );
    return;
  }

  try {
    const opensarlabdiskspaceWidget: DiskSpaceWidget = new DiskSpaceWidget(
      settings
    );
    opensarlabdiskspaceWidget.id = widget_id;

    app.shell.add(opensarlabdiskspaceWidget as any, widgetPlacement, {
      rank: rank
    });

    console.log(
      'JupyterLab extension opensarlab-frontend:diskspace is activated!'
    );
  } catch (reason) {
    console.error(
      `Error on GET /opensarlab-frontend/opensarlab-diskspace.\n${reason}`
    );
  }
}
