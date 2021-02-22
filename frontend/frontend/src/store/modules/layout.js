import http from '@/utils/request'
import port from '@/utils/api'
import constants from '@/utils/constants'
// import visual from '@/api/visual.js'

const state = {
  stateStore: {},
  category: [],
  initShowPanel: '',
  initSidebarId: '',
  categoryIndex: '',
  runFileCategory: '',
  userSelectRunFile: '',
  runCategoryDetail: '',
  multipleFlag: '',
  svgDownloadList: [],
  // timerId: {
  //   overallTimerId: null,
  //   subCategoryTimerId: null
  // }
  subCategoryTimerId: null,
  initWaitingMessage: '',
  timeSyncInterval: '',
  errorMessage: '',
  params: {
    id: '',
    trainJobName: ''
  }
}

const getters = {
  allCategoryInform: (state) => state.category,
  initShowPanelInfo: (state) => state.initShowPanel,
  initRunFile: (state) => state.runFileCategory,
  initWaitingMessage: (state) => state.initWaitingMessage,
  getParams: (state) => state.params,
  getErrorMessage: (state) => state.errorMessage,
  setDownloadSvgClass: (state) => state.svgDownloadList,
  getStateStore: (state) => state.stateStore
}

const actions = {
  async initWaitingPage(context, params) {
    // context.commit('setWaitingMessage', 'success')
    // 暂时没有后端接口使用延迟
    // params = { 'id': 'test' }
    await http.useGet('/api/init', params)
      .then(res => {
        console.log(res)
        context.commit('setCookie', 'session_id', res.data.data['session_id'])
        context.commit('setWaitingMessage', res.data.data['msg'])
        // context.state.waitingPage = res.data['msg']
      })
  },
  async initFeatchCategory(context, path) {
    // console.log(visual)
    const splitArray = path.split('/')
    const cate = splitArray[splitArray.length - 1]
    await http.useGet(port.manage.initCategory, {}).then(res => {
    // await visual.getCategory().then(res => {
      // console.log(res)
      // res.data.code
      // res.data.msg
      const dataCategoryInfo = res.data.data
      let categorys = []
      const runFile = []
      const categoryToRunFile = {} // 根据所选类目显示run信息
      Object.keys(dataCategoryInfo).forEach(val => {
        categorys = categorys.concat(Object.keys(dataCategoryInfo[val]).filter(v => !categorys.includes(v)))
        runFile.push(val)
      })
      const categoryOrder = []
      categorys.forEach(val => {
        categoryOrder.push(constants.CATEGORYORDER.indexOf(val))
      })
      categoryOrder.sort()
      let newIndex = 0
      if (cate === 'index') {
        newIndex = 0
      } else {
        newIndex = categoryOrder.indexOf(constants.CATEGORYORDER.indexOf(cate))
      }
      if (categorys.length !== 0) {
        categorys.forEach(ce => {
          const detailTag = []
          const tempRunFile = []
          const temp = []
          runFile.forEach(res => {
            if (dataCategoryInfo[res].hasOwnProperty(ce)) {
              tempRunFile.push(res)
              detailTag.push(dataCategoryInfo[res][ce])
              temp.push(res)
            }
            categoryToRunFile[ce] = temp
          })
          if (ce === constants.CATEGORYORDER[categoryOrder[0]] && cate === 'index') {
            context.dispatch(
              '' + ce + '/getSelfCategoryInfo',
              [tempRunFile, detailTag, { 'initStateFlag': true }],
              { root: true })
          } else if (ce === cate) {
            context.dispatch(
              '' + ce + '/getSelfCategoryInfo',
              [tempRunFile, detailTag, { 'initStateFlag': true }],
              { root: true })
          } else {
            context.dispatch(
              '' + ce + '/getSelfCategoryInfo',
              [tempRunFile, detailTag, { 'initStateFlag': false }],
              { root: true })
          }
        })
      } else {
        context.commit('setErrorMessage', '日志文件中尚未发现可展示信息！' + '_' + new Date().getTime())
      }
      context.commit('setRunCategoryDetail', categoryToRunFile)
      context.commit('setCategory', [categoryOrder, newIndex]) // [0, 1, 2, 3, 4, 5, 6, 7, 8]
      context.commit('setRunCategory', constants.CATEGORYORDER[categoryOrder[newIndex]]) // [".", 'train', 'vgg']
    })
  },
  async timingFeatchCategory(context, parm) { // parm 存储间隔时间
    const splitArray = parm[1].split('/')
    const cate = splitArray[splitArray.length - 1]
    const t = setInterval(() => {
      http.useGet(port.manage.initCategory, { test: 1 }).then(res => {
        // context.commit('setCategory', res.data)
        const dataCategoryInfo = res.data.data
        let categorys = []
        const runFile = []
        const categoryToRunFile = {} // 根据所选类目显示run信息
        Object.keys(dataCategoryInfo).forEach(val => {
          categorys = categorys.concat(Object.keys(dataCategoryInfo[val]).filter(v => !categorys.includes(v)))
          runFile.push(val)
        })
        const categoryOrder = []
        categorys.forEach(val => {
          categoryOrder.push(constants.CATEGORYORDER.indexOf(val))
        })
        categoryOrder.sort()
        let newIndex = 0
        if (cate === 'index') {
          newIndex = 0
        } else {
          newIndex = categoryOrder.indexOf(constants.CATEGORYORDER.indexOf(cate))
        }
        if (categorys.length !== 0) {
          categorys.forEach(ce => {
            const detailTag = []
            const tempRunFile = []
            const temp = []
            runFile.forEach(res => {
              if (dataCategoryInfo[res].hasOwnProperty(ce)) {
                tempRunFile.push(res)
                detailTag.push(dataCategoryInfo[res][ce])
                temp.push(res)
              }
              categoryToRunFile[ce] = temp
            })
            if (ce === constants.CATEGORYORDER[categoryOrder[0]] && cate === 'index') {
              context.dispatch(
                '' + ce + '/getSelfCategoryInfo',
                [tempRunFile, detailTag, { 'initStateFlag': true }],
                { root: true })
            } else if (ce === cate) {
              context.dispatch(
                '' + ce + '/getSelfCategoryInfo',
                [tempRunFile, detailTag, { 'initStateFlag': true }],
                { root: true })
            } else {
              context.dispatch(
                '' + ce + '/getSelfCategoryInfo',
                [tempRunFile, detailTag, { 'initStateFlag': false }],
                { root: true })
            }
          })
        } else {
          context.commit('setErrorMessage', '日志文件中尚未发现可展示信息！' + '_' + new Date().getTime())
        }
        context.commit('setRunCategoryDetail', categoryToRunFile) // 是保留这个么？？？Qu
        context.commit('setCategory', [categoryOrder, newIndex]) // [0, 1, 2, 3, 4, 5, 6, 7, 8]
        context.commit('setRunCategory', constants.CATEGORYORDER[categoryOrder[newIndex]]) // [".", 'train', 'vgg']
      })
    }, parm[0])
    context.commit('setSyncTime', t)
  },
  async timingFeatchCategoryOnce(context, parm) {
    const splitArray = parm.split('/')
    const cate = splitArray[splitArray.length - 1]
    await http.useGet(port.manage.initCategory, {}).then(res => {
    // await visual.getCategory().then(res => {
      const dataCategoryInfo = res.data.data
      let categorys = []
      const runFile = []
      const categoryToRunFile = {} // 根据所选类目显示run信息
      Object.keys(dataCategoryInfo).forEach(val => {
        categorys = categorys.concat(Object.keys(dataCategoryInfo[val]).filter(v => !categorys.includes(v)))
        runFile.push(val)
      })
      const categoryOrder = []
      categorys.forEach(val => {
        categoryOrder.push(constants.CATEGORYORDER.indexOf(val))
      })
      categoryOrder.sort()
      let newIndex = 0
      if (cate === 'index') {
        newIndex = 0
      } else {
        newIndex = categoryOrder.indexOf(constants.CATEGORYORDER.indexOf(cate))
      }
      if (categorys.length !== 0) {
        categorys.forEach(ce => {
          const detailTag = []
          const tempRunFile = []
          const temp = []
          runFile.forEach(res => {
            if (dataCategoryInfo[res].hasOwnProperty(ce)) {
              tempRunFile.push(res)
              detailTag.push(dataCategoryInfo[res][ce])
              temp.push(res)
            }
            categoryToRunFile[ce] = temp
          })
          if (ce === constants.CATEGORYORDER[categoryOrder[0]] && cate === 'index') {
            context.dispatch(
              '' + ce + '/getSelfCategoryInfo',
              [tempRunFile, detailTag, { 'initStateFlag': true }],
              { root: true })
          } else if (ce === cate) {
            context.dispatch(
              '' + ce + '/getSelfCategoryInfo',
              [tempRunFile, detailTag, { 'initStateFlag': true }],
              { root: true })
          } else {
            context.dispatch(
              '' + ce + '/getSelfCategoryInfo',
              [tempRunFile, detailTag, { 'initStateFlag': false }],
              { root: true })
          }
        })
      } else {
        context.commit('setErrorMessage', '日志文件中尚未发现可展示信息！' + '_' + new Date().getTime())
      }
      context.commit('setRunCategoryDetail', categoryToRunFile)
      context.commit('setCategory', [categoryOrder, newIndex]) // [0, 1, 2, 3, 4, 5, 6, 7, 8]
      context.commit('setRunCategory', constants.CATEGORYORDER[categoryOrder[newIndex]]) // [".", 'train', 'vgg']
    })
  },
  async getClickState(context, parm) {
    context.state.categoryIndex.forEach(value => {
      const el = constants.CATEGORYORDER[value]
      if (value === parm) {
        context.commit('' + el + '/setClickState', true, { root: true })
      } else {
        context.commit('' + el + '/setClickState', false, { root: true })
      }
    })
  }
}

const mutations = {
  setParams: (state, params) => {
    state.params = params
  },
  setCookie: (state, name, value) => {
    var days = 14
    var exp = new Date()
    exp.setTime(exp.getTime() + days * 24 * 60 * 60 * 1000)
    document.cookie = name + '=' + escape(value) + ';expires=' + exp.toGMTString() + '; path=/'
  },
  setCategory: (state, value) => {
    state.categoryIndex = value[0]
    const CategoryInfomation = []
    Array.from(value[0]).forEach((order, index) => {
      CategoryInfomation.push({
        id: index,
        rawName: constants.CATEGORYORDER[order],
        routerName: '/index/' + constants.CATEGORYORDER[order],
        name: constants.CATEGORY[order][3],
        nameCopy: constants.CATEGORY[order][3],
        icon: constants.CATEGORY[order][4],
        iconCopy: constants.CATEGORY[order][4]
      })
    })
    state.category = CategoryInfomation
    state.initSidebarId = value[1]
    if (state.initShowPanel !== CategoryInfomation[value[1]]) {
      state.initShowPanel = CategoryInfomation[value[1]]
    }
    const download = {}
    state.category.forEach(val => {
      download[val.rawName] = []
      if (val.rawName === 'graph') {
        download['graph'].push('#svg-canvas')
      }
    })
    state.svgDownloadList = download
  },
  setSyncTime: (state, value) => {
    state.timeSyncInterval = value
  },
  clearSync: (state) => {
    clearInterval(state.timeSyncInterval)
  },
  setWaitingMessage: (state, value) => {
    state.initWaitingMessage = value
  },
  setRunCategory: (state, value) => { // value 为类目信息
    let detailInfo = []
    let initOption = []
    let temp = ''
    state.runCategoryDetail[value].forEach((val, i) => {
      detailInfo.push({
        'value': val,
        'label': val
      })
      if (constants.RUNFILESHOWFlAG[value] === 0) {
        temp = false
        if (i === 0) {
          initOption = val
        }
      } else {
        initOption.push(val)
        temp = true
      }
      if (constants.RUNFILESHOWFlAG[value] === 2) {
        detailInfo = []
        initOption = []
        temp = 2
      }
    })
    if (value in state.stateStore) {
      state.userSelectRunFile = state.stateStore[value]
    } else {
      state.stateStore[value] = initOption
      state.userSelectRunFile = initOption
    }
    state.runFileCategory = detailInfo
    state.multipleFlag = temp
  },
  setUserSelectRunFile: (state, value) => {
    state.userSelectRunFile = value
  },
  setRunCategoryDetail: (state, value) => {
    state.runCategoryDetail = value
  },
  setTimer: (state, value) => {
    state.subCategoryTimerId = value
  },
  setErrorMessage: (state, param) => {
    state.errorMessage = param
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
