export interface IProjectStep {
  id: string;
  key: string;
  title: string;
  name: string;
  description: string;
  path: string;
  missionId: string;
  parentId: string;
  isChapter: boolean;
  progress: number;
  children?: IProjectStep[];
}
