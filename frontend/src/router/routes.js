const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'dashboard', name:'dashboard', component: () => import('pages/DashboardPage.vue') },
      { path: 'estados', name:'estados', component: () => import('pages/EstadosPage.vue') },
      { path: 'municipios', name:'municipios', component: () => import('pages/MunicipiosPage.vue') },
      { path: 'medicos', name:'medicos', component: () => import('pages/MedicosPage.vue') },
      { path: 'hospitais', name:'hospitais', component: () => import('pages/HospitaisPage.vue') },
      { path: 'cid', name:'cid', component: () => import('pages/CidPage.vue') },
      { path: 'pacientes', name:'pacientes', component: () => import('pages/PacientesPage.vue') },
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
