/* eslint-disable no-unused-vars */
/*
 * @Description: state.graph
 * @version: 1.0
 * @Author: xds
 * @Date: 2020-05-02 07:09:25
 * @LastEditors: xds
 * @LastEditTime: 2020-05-25 13:10:26
 */
import http from '@/utils/request'
import port from '@/utils/api'

const state = {
  sInitState: 0,
  srcData: [],
  graphData: '', // 具体数据
  runName: [],
  tagName: [],
  retList: '',
  clear: 0,
  info: '',
  reg: '',
  run: 0,
  hidden_: 0,
  pre: 0,
  clickDel: [],
  modifyClick: '',
  curTag: '',
  runChangeTag: false,
  isDrawing: false,
  list: []
}

const getters = {
  getGraphData: (state) => state.graphData,
  getRetList: (state) => state.retList,
  getReg: (state) => state.reg,
  getClear: (state) => state.clear,
  getInfo: (state) => state.info,
  getHidden: (state) => state.hidden_,
  getRun: (state) => state.run,
  getPre: (state) => state.pre,
  getClick: (state) => state.clickDel,
  getModifyClick: (state) => state.modifyClick,
  getRunName: (state) => state.runName,
  getTagName: (state) => state.tagName,
  getCurTag: (state) => state.curTag,
  getRunChangeTag: (state) => state.runChangeTag,
  getIsDrawing: (state) => state.isDrawing,
  getSList: (state) => state.list,
  getInitOption: (state) => state.sInitState
}

const actions = {
  async getSelfCategoryInfo(context, param) { // param数据形式
    context.commit('setSelgCategoryInfo', param)// showGrap，是否有图
    if (param[2]['initStateFlag']) { // 如果是第一个组件，马上取出数据，渲染组件
      const param1 = { run: context.state.runName[0], tag: context.state.tagName[0][0] }
      // context.dispatch('getData', param1)
    }
  },
  async getFullData(context, param) { // 请求数据，param需要向后端传递什么参数
    state.sInitState = 0
    if (param.tag === 'c_graph') {
      http.useGet(port.category.graph, param).then(res => {
        const data = JSON.parse(res.data.data)
        console.log(data)
        context.commit('setGraphData', data['net'])
        context.commit('setRetList', data['operator'])
      })
    } else {
      http.useGet(port.category.graph, param).then(res => {
        const data = JSON.parse(res.data.data)
        context.commit('setSrcData', data['net'])
        context.commit('setGraphData', data['net'][0])
        context.commit('setOptionList', data['net'].length)
        context.commit('setRetList', data['operator'])
      })
    }
  }
}

const mutations = {
  setOptionList: (state, param) => {
    const optionList = []
    for (let i = 0; i < param; i++) {
      const item = {}
      item.value = i
      item.label = '结构图' + i
      optionList.push(item)
    }
    state.list = optionList
  },
  setSrcData: (state, param) => {
    state.srcData = param
  },
  setSelgCategoryInfo: (state, param) => { // 存run和tag
    // state.showGrap = param
    state.runName = param[0]
    state.tagName = param[1]
    state.curTag = state.tagName[0][0]
  },
  setGraphData: (state, param) => {
    state.graphData = param
  },
  setRetList: (state, param) => {
    state.retList = param
  },
  Clear: (state) => {
    ++state.clear
  },
  getNodeInfo: (state, param) => {
    state.info = param
  },
  regularEx: (state, param) => {
    state.reg = param
  },
  Run: (state) => {
    ++state.run
  },
  Hidden: (state) => {
    ++state.hidden_
  },
  Pre: (state) => {
    ++state.pre
  },
  getClickDel: (state, param) => {
    state.clickDel = param
    // console.log(param)
  },
  Modify: (state, param) => {
    state.modifyClick = param
  },
  setCurTag: (state, param) => {
    state.curTag = param
  },
  setRunChangeTag: (state, param) => {
    state.runChangeTag = param
  },
  setIsDrawing: (state, param) => {
    state.isDrawing = param
  },
  setData: (state, param) => {
    if (state.curTag === 's_graph') {
      console.log(param)
      state.graphData = state.srcData[param]
      state.sInitState = param
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
