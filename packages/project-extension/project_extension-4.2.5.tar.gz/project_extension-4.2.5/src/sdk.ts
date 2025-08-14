import Axios from 'axios';
import { getAuthUrl, parseProjectRes } from './util';
import { loginDialog } from './dialog';
const apiUrl = '/poros/api';
const axios = Axios.create({});
axios.interceptors.request.use(config => {
  if (localStorage.getItem('sp-token')) {
    config.headers.Authorization = `Bearer ${localStorage.getItem('sp-token')}`;
  }
  console.log('---request', config);
  return config;
});

axios.interceptors.response.use(
  res => {
    console.log('---response', res);
    return res;
  },
  error => {
    console.log('---error', error);
    const status = error?.response?.status;
    switch (status) {
      case 401:
        // console.warn('未授权，请重新登录');
        // window.location.href = '/login';
        // 可触发登出逻辑
        loginDialog().then((value: any) => {
          console.log(value);
          console.log(' authurl', getAuthUrl());
          if (value.button.label === '去登录') {
            window.location.href = getAuthUrl();
          }
        });
        break;
      case 404:
        console.warn('请求资源不存在');
        break;
      case 500:
        console.error('服务器内部错误');
        break;
      default:
        console.warn('网络异常，请稍后再试');
    }
    return Promise.reject(error);
  }
);
/**
 * 根据 项目ID 获取项目指导
 * @param projectId
 * @returns
 */
export const getProjectMissions = (projectId: string) => {
  return axios
    .get(`${apiUrl}/projects/${projectId}/jupyter`)
    .then((res: any) => {
      console.log('---getProject Missions', res);
      return parseProjectRes(res.data.data);
    });
};

export const updateProjectMission = (projectId?: string, data?: any) => {
  if (!data.id) {
    return axios
      .post(`${apiUrl}/project_missions/`, {
        name: data.name,
        projectId,
        parentId: data.parentId
      })
      .then((res: any) => {
        console.log('---createProjectMission', res);
        return res.data.data;
      });
  } else {
    console.log('---updateProjectMission', data);
    return axios
      .patch(`${apiUrl}/project_missions/${data.id}`, {
        ...data
      })
      .then((res: any) => {
        console.log('---updateProjectMission', res);
        return res.data.data;
      });
  }
};

export const updateMissionFile = (data: any) => {
  return axios.post(`${apiUrl}/jupyters`, {
    missionId: data.missionId,
    path: data.path
  });
};

export const deleteProjectMission = (missionId?: string) => {
  return axios
    .delete(`${apiUrl}/project_missions/${missionId}`)
    .then((res: any) => {
      console.log('---deleteProjectMission', res);
      return res.data.data;
    });
};
