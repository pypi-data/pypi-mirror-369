import { IProjectStep } from './type';
import { PageConfig } from '@jupyterlab/coreutils';
// import { PointerIcon } from './pointerIcon';
function parseStep(data: any, mission: any): IProjectStep {
  const file = data.jupyterList?.find((f: any) => f.missionId === mission.id);
  const progressItem = data.progressList?.find(
    (p: any) => p.missionId === mission.id
  );
  return {
    id: mission.id,
    key: mission.id,
    name: mission.name,
    title: mission.name,
    description: mission.description,
    path: file?.path,
    progress: progressItem?.progress_percentage,
    missionId: mission.id,
    parentId: mission.parentId,
    isChapter: !mission.parentId,
    children:
      data.missions
        .filter((item: any) => item.parentId === mission.id)
        ?.map((item: any) => parseStep(data, item)) || []
  };
}

export function parseProjectRes(data: any): IProjectStep[] {
  const steps: IProjectStep[] = [];
  const missions = data.missions;
  if (missions && missions.length) {
    missions
      .filter((item: any) => !item.parentId)
      .forEach((mission: any) => {
        const step: IProjectStep = parseStep(data, mission);
        steps.push(step);
      });
    return steps;
  } else {
    return [];
  }
}

export function getAuthUrl(): string {
  const envConfig = JSON.parse(PageConfig.getOption('env') || '{}');
  console.log('Environment Config:', envConfig);
  const auth_url = envConfig['AUTH_URL'] || '';
  return auth_url;
}
