import { defineBoot } from '#q-app/wrappers'
import axios from 'axios'

const api = axios.create({
  baseURL: 'https://tender-cows-reply.loca.lt/',
})

export default defineBoot(({ app }) => {

  app.config.globalProperties.$axios = axios

  app.config.globalProperties.$api = api
})

export { api }
