import { ref, reactive, computed } from "vue";
import { defineStore } from "pinia";
import * as collector from "../api/collector"



export const useRulesStore = defineStore("rules", () => {
  const rules: any[] = reactive([])

  async function loadRules() {
    let res = await collector.getRules()
    console.log(res)
    rules.length = 0
    rules.push(...res.rules)
  }


  async function addRules(rule: any[]) {
    let res = await collector.addRules(rule)
    rules.length = 0
    rules.push(...res.rules)
  }

  const orderedRules = computed(() => [...rules].sort((a,b) => b.tweet_count - a.tweet_count))

  return { rules, loadRules, orderedRules, addRules };
});
