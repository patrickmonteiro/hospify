<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title class="text-bold">
          Hospify
        </q-toolbar-title>

      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
      <q-list>
        <q-item-label
          header
        >
          Menu Principal
        </q-item-label>

        <q-item clickable v-ripple exact :to="{ name: 'estados' }">
          <q-item-section avatar>
            <q-icon name="mdi-flag"  />
          </q-item-section>
          <q-item-section class="text-bold text-lg">
            Estado
          </q-item-section>
        </q-item>

        <q-item clickable v-ripple :to="{ name: 'municipios' }">
          <q-item-section avatar>
            <q-icon name="mdi-flag-variant-plus-outline"  />
          </q-item-section>
          <q-item-section class="text-bold text-lg">
            Municípios
          </q-item-section>
        </q-item>

        <q-item clickable v-ripple>
          <q-item-section avatar>
            <q-icon name="mdi-hospital-box"  />
          </q-item-section>
          <q-item-section class="text-bold text-lg">
            CID-10
          </q-item-section>
        </q-item>

        <q-item clickable v-ripple>
          <q-item-section avatar>
            <q-icon name="mdi-doctor"  />
          </q-item-section>
          <q-item-section class="text-bold">
            Médicos
          </q-item-section>
        </q-item>

        <q-item clickable v-ripple>
          <q-item-section avatar>
            <q-icon name="mdi-hospital-building"  />
          </q-item-section>
          <q-item-section class="text-bold">
            Hospitais
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'

const leftDrawerOpen = ref(false)

function toggleLeftDrawer () {
  leftDrawerOpen.value = !leftDrawerOpen.value
}
</script>
