import { ref, reactive, computed } from "vue";
import { defineStore } from "pinia";

export const useRulesStore = defineStore("rules", () => {
  const rules: any[] = reactive([]);
  const apiStreamerRules: any[] = reactive([])

  function loadRules() {
    console.log('lolo')
    rules.length = 0

    let remote = [
      {"id":1,"type":"searcher","name":"Searcher_Hiking","tag":"Hiking","query":"#hiking","tweet_ids":[],"tweet_count":821},{"id":2,"type":"streamer","name":"Customized Name for identification","tag":"Rule","query":"#hiking OR #nature OR #mountains OR picture","tweet_ids":[],"tweet_count":46},{"id":3,"type":"streamer","name":"Streamer_Other","tag":"Other","query":"#cats OR picture","tweet_ids":[],"tweet_count":14391},{"id":4,"type":"streamer","name":"Gouzi gouzi","tag":"Bubble","query":"#bulbbe OR #bath","tweet_ids":[],"tweet_count":7},{"id":5,"type":"searcher","name":"Round Or Not","tag":"Circle","query":"#circle #math #smart","tweet_ids":[],"tweet_count":0},{"id":6,"type":"searcher","name":"Round Or Not","tag":"Circle","query":"#circle OR #math OR #smart","tweet_ids":[],"tweet_count":112},{"id":7,"type":"searcher","name":"Round Or Not","tag":"Circle","query":"#circle OR #math OR #smart OR cirlce OR round OR curve","tweet_ids":[],"tweet_count":1211},{"id":8,"type":"streamer","name":"test name","tag":"Testing","query":"pls OR test OR me","tweet_ids":[],"tweet_count":0},{"id":9,"type":"streamer","name":"test name","tag":"Testing","query":"(pls OR test OR me)","tweet_ids":[],"tweet_count":0},{"id":10,"type":"streamer","name":"test name","tag":"Testing","query":"#pls OR #test OR #me","tweet_ids":[],"tweet_count":0},{"id":11,"type":"streamer","name":"Gouzi gouzi","tag":"default","query":"#bulbbe OR #bath","tweet_ids":[],"tweet_count":0},{"id":12,"type":"streamer","name":"Streamer_Other","tag":"default","query":"#cats OR picture","tweet_ids":[],"tweet_count":0},{"id":13,"type":"streamer","name":"test name","tag":"default","query":"pls OR test OR me","tweet_ids":[],"tweet_count":0},{"id":14,"type":"streamer","name":"gui rule","tag":"default","query":"#maboi","tweet_ids":[],"tweet_count":0},{"id":16,"type":"streamer","name":"test","tag":"test","query":"test","tweet_ids":[],"tweet_count":0}
      ]
    rules.push(...remote)

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

  return { rules, loadRules, orderedRules, apiStreamerRules };
});
