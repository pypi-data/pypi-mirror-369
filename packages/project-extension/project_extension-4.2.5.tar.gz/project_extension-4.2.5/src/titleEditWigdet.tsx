import { ReactWidget } from '@jupyterlab/apputils';
import React, { useState } from 'react';
import { IProjectStep } from './type';
const TitleWidget = ({
  nodeData,
  valueChange
}: {
  nodeData?: Partial<IProjectStep>;
  valueChange?: (value: string) => void;
}) => {
  const [title, setTitle] = useState(nodeData?.title);
  return (
    <div>
      <input
        value={title}
        onChange={e => {
          setTitle(e.target.value);
          valueChange && valueChange(e.target.value);
        }}
      />
    </div>
  );
};
export class TitleEditWidget extends ReactWidget {
  private nodeData: Partial<IProjectStep>;
  constructor(nodeData?: Partial<IProjectStep>) {
    super();
    this.id = 'project-title-edit-widget';
    // this.addClass('project-sidebar-widget');
    // this.title.closable = true;
    // this.title.iconLabel = '项目步骤';
    // this.title.caption = '打开项目步骤';
    // this.commands = commands;
    this.nodeData = nodeData
      ? {
          ...nodeData
        }
      : { name: '', title: '' };
  }
  public getValue(): Partial<IProjectStep> | undefined {
    return this.nodeData;
  }
  protected render(): React.JSX.Element {
    return (
      <TitleWidget
        nodeData={this.nodeData}
        valueChange={value => {
          this.nodeData.name = value;
          this.nodeData.title = value;
        }}
      />
    );
  }
}
