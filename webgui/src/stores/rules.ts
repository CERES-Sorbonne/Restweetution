import { ref, reactive, computed } from "vue";
import { defineStore } from "pinia";
import * as collector from "../api/collector"



export const useRulesStore = defineStore("rules", () => {
  const rules: any[] = reactive([]);
  const apiStreamerRules: any[] = reactive([])

  async function loadRules() {
    let res = await collector.getRules()
    console.log(res)
    rules.length = 0
    rules.push(...res.rules)
    loadAPIStreamerRules()
  }

  function loadAPIStreamerRules() {
    let remote = [
      {query: '#hiking', tag:'Hiking', api_id: '1234949343983948'},
      {query: '#cats OR picture', tag:'Cat,Picture', api_id: '1234949343983948'}
    ]

    apiStreamerRules.push(...remote)
  }

  const orderedRules = computed(() => [...rules].sort((a,b) => b.tweet_count - a.tweet_count))
  const streamerRules = computed(() => orderedRules.value.filter((r) => r.type == 'streamer'))

  return { rules, loadRules, orderedRules, apiStreamerRules, streamerRules };
});
