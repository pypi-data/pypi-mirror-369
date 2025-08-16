import { JupyterFrontEnd } from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { PartialJSONObject } from '@lumino/coreutils';

import { find } from '@lumino/algorithm';

import { Widget } from '@lumino/widgets';

import { requestAPI } from './handler';
import toastr from 'toastr';

/*
    Particular toast event
*/
interface IButter {
  title: string;
  message: string;
  type: string;
  severity: Partial<number>;
}

/*
    Toast options and an array of toast events
*/
interface IBread {
  options: object;
  data: Array<IButter>;
}

class OpensarlabNotifyWidget extends Widget {
  constructor() {
    super();

    this.toastrLink = document.createElement('link');
    this.toastrLink.rel = 'stylesheet';
    this.toastrLink.href =
      'https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css';
    this.node.appendChild(this.toastrLink);

    document.head.insertAdjacentHTML(
      'beforeend',
      '<style>#toast-container>div{opacity:1;}</style>'
    );
  }

  readonly toastrLink: HTMLLinkElement;

  makeToast(notes: IBread) {
    toastr.options = notes.options;
    notes.data.forEach((entry: any) => {
      (toastr as any)[entry.type](entry.message, entry.title);
    });
  }

  notifications(note_types: string) {
    requestAPI<any>(`opensarlab-oslnotify?type=${note_types}`)
      .then((notes: IBread) => {
        this.makeToast(notes);
      })
      .catch((reason: string) => {
        console.log(
          `Error on GET /opensarlab-frontend/opensarlab-oslnotify.\n${reason}`
        );
      });
  }
}

export async function main(
  app: JupyterFrontEnd,
  allSettings: ISettingRegistry.ISettings
): Promise<void> {
  const settings =
    (allSettings.get('oslnotify').composite as PartialJSONObject) ??
    (allSettings.default('oslnotify') as PartialJSONObject);

  const enabled = settings.enabled as boolean;
  const note_type = settings.note_type as string;

  const widget_id = 'opensarlab-notify-widget';

  const widget = find(app.shell.widgets('top'), w => w.id === widget_id);
  if (widget) {
    widget.dispose();
  }

  if (!enabled) {
    console.log(
      'JupyterLab extension opensarlab-frontend:oslnotify is not activated!'
    );
    return;
  }

  const opensarlabNotifyWidget = new OpensarlabNotifyWidget();
  opensarlabNotifyWidget.id = widget_id;
  opensarlabNotifyWidget.notifications(note_type);

  app.shell.add(opensarlabNotifyWidget as any, 'top', { rank: 1999 });

  console.log(
    'JupyterLab extension opensarlab-frontend:oslnotify is activated!'
  );
}
